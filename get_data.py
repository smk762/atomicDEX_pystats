#!/usr/bin/env python3

# Gets data via DEXP2P
# komodo-cli -ac_name=DEXP2P DEX_list "" 0 "swaps"	

import os
import re
import sys
import json
import http
import time
import codecs
import requests
import platform
from slickrpc import Proxy
from os.path import expanduser

cwd = os.getcwd()
home = expanduser("~")

# TODO: check this is up to date 
maker_success_events = ['Started', 'Negotiated', 'TakerFeeValidated', 'MakerPaymentSent', 'TakerPaymentReceived', 'TakerPaymentWaitConfirmStarted',
                        'TakerPaymentValidatedAndConfirmed', 'TakerPaymentSpent', 'Finished']

maker_errors_events = ['StartFailed', 'NegotiateFailed', 'TakerFeeValidateFailed', 'MakerPaymentTransactionFailed', 'MakerPaymentDataSendFailed',
                      'TakerPaymentValidateFailed', 'TakerPaymentSpendFailed', 'MakerPaymentRefunded', 'MakerPaymentRefundFailed']

taker_success_events = ['Started', 'Negotiated', 'TakerFeeSent', 'MakerPaymentReceived', 'MakerPaymentWaitConfirmStarted',
                        'MakerPaymentValidatedAndConfirmed', 'TakerPaymentSent', 'TakerPaymentSpent', 'MakerPaymentSpent', 'Finished']

taker_errors_events = ['StartFailed', 'NegotiateFailed', 'TakerFeeSendFailed', 'MakerPaymentValidateFailed', 'TakerPaymentTransactionFailed',
                      'TakerPaymentDataSendFailed', 'TakerPaymentWaitForSpendFailed', 'MakerPaymentSpendFailed', 'TakerPaymentRefunded',
                      'TakerPaymentRefundFailed']


# Set coin config locations. Not yet tested outside Linux for 3rd party coins!
operating_system = platform.system()
if operating_system == 'Darwin':
    ac_dir = home + '/Library/Application Support/Komodo'
elif operating_system == 'Linux':
    ac_dir = home + '/.komodo'
elif operating_system == 'Win64' or operating_system == 'Windows':
    ac_dir = '%s/komodo/' % os.environ['APPDATA']
    import readline

def def_creds(chain):
    rpcport =''
    coin_config_file = ''
    if chain == 'KMD':
        coin_config_file = str(ac_dir + '/komodo.conf')
    elif chain == 'BTC':
        coin_config_file = str(home + '/.bitcoin/bitcoin.conf')       
    else:
        coin_config_file = str(ac_dir + '/' + chain + '/' + chain + '.conf')
    with open(coin_config_file, 'r') as f:
        for line in f:
            l = line.rstrip()
            if re.search('rpcuser', l):
                rpcuser = l.replace('rpcuser=', '')
            elif re.search('rpcpassword', l):
                rpcpassword = l.replace('rpcpassword=', '')
            elif re.search('rpcport', l):
                rpcport = l.replace('rpcport=', '')
    if len(rpcport) == 0:
        if chain == 'KMD':
            rpcport = 7771
        elif chain == 'KMD':
            rpcport = 8333
        else:
            print("rpcport not in conf file, exiting")
            print("check "+coin_config_file)
            exit(1)
    return(Proxy("http://%s:%s@127.0.0.1:%d"%(rpcuser, rpcpassword, int(rpcport))))


def get_local_uuids(role):
    uuids_list_tmp = os.listdir(role)
    uuids_list = []
    for uuid in uuids_list_tmp:
        if uuid[-5:] == '.json':
            uuids_list.append(uuid[:-5])
    return uuids_list

folders = ["MAKER","TAKER", "UNKNOWN"]
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)

def get_role(swap_json):
    if 'TakerFeeValidated' in swap_json['success_events']:
        return 'MAKER'        
    elif 'TakerFeeSent' in swap_json['success_events']:
        return 'TAKER'
    else:
        return 'UNKNOWN'


rpc = def_creds("DEXP2P")

uuids = {}
for folder in folders:
    uuids[folder] = get_local_uuids(folder)
print(uuids)
json_data = rpc.DEX_list("", '0', "swaps")
print(json_data)
for swap in json_data['matches']:
    swap_json = json.loads(swap['payload'])
    uuid = swap_json['uuid']
    role = get_role(swap_json)
    if uuid not in uuids[role]:
        print("Adding ["+uuid+"] ["+role+"]")
        with open(role+"/"+uuid+".json", "w+") as f:
            json.dump(swap_json, f)
    else:
        print("["+role+"] ["+uuid+"] already saved")
