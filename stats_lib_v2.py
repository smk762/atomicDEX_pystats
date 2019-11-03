#!/usr/bin/env python3
import os
import json
import bitcoin
from bitcoin.wallet import P2PKHBitcoinAddress
from bitcoin.core import x
from bitcoin.core import CoreMainParams
from datetime import datetime, timezone
from os import listdir
from os.path import isfile, join

json_path = '/var/www/html/json'

maker_success_events = ['Started', 'Negotiated', 'TakerFeeValidated', 'MakerPaymentSent', 'TakerPaymentReceived', 'TakerPaymentWaitConfirmStarted',
                        'TakerPaymentValidatedAndConfirmed', 'TakerPaymentSpent', 'Finished']

maker_errors_events = ['StartFailed', 'NegotiateFailed', 'TakerFeeValidateFailed', 'MakerPaymentTransactionFailed', 'MakerPaymentDataSendFailed',
                      'TakerPaymentValidateFailed', 'TakerPaymentSpendFailed', 'MakerPaymentRefunded', 'MakerPaymentRefundFailed']

taker_success_events = ['Started', 'Negotiated', 'TakerFeeSent', 'MakerPaymentReceived', 'MakerPaymentWaitConfirmStarted',
                        'MakerPaymentValidatedAndConfirmed', 'TakerPaymentSent', 'TakerPaymentSpent', 'MakerPaymentSpent', 'Finished']

taker_errors_events = ['StartFailed', 'NegotiateFailed', 'TakerFeeSendFailed', 'MakerPaymentValidateFailed', 'TakerPaymentTransactionFailed',
                      'TakerPaymentDataSendFailed', 'TakerPaymentWaitForSpendFailed', 'MakerPaymentSpendFailed', 'TakerPaymentRefunded',
                      'TakerPaymentRefundFailed']
debug = False
# DEBUGGING AND CONSOLE READOUT
def colorize(string, color):
        colors = {
                'black':'\033[30m',
                'red':'\033[31m',
                'green':'\033[32m',
                'orange':'\033[33m',
                'blue':'\033[34m',
                'purple':'\033[35m',
                'cyan':'\033[36m',
                'lightgrey':'\033[37m',
                'darkgrey':'\033[90m',
                'lightred':'\033[91m',
                'lightgreen':'\033[92m',
                'yellow':'\033[93m',
                'lightblue':'\033[94m',
                'pink':'\033[95m',
                'lightcyan':'\033[96m',
        }
        if color not in colors:
            return str(string)
        else:
            return colors[color] + str(string) + '\033[0m'

def debug_print(msg, debug_on=False):
    if debug_on:
        print(msg)
        print()
    if debug_on == 'wait':
        print(msg)
        print()
        input()

# ADDRESS TRANSLATION (sometimes does not work)
class CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 60,
                       'SCRIPT_ADDR': 85,
                       'SECRET_KEY': 188}
bitcoin.params = CoinParams

def get_radd_from_pub(pub):
    try:
        addr = str(P2PKHBitcoinAddress.from_pubkey(x(pub)))
    except Exception as e:
        try:
            addr = str(P2PKHBitcoinAddress.from_pubkey(x(pub)))
        except Exception as e:
            print(colorize(str(e)+": "+pub, 'red'))
            print(e)
            addr = pub
            pass
        pass
    return str(addr)

# TUI STUFF 

def get_ts(interrogative):
    start_date = input(interrogative+" [format: DD/MM/YYYY]: ")
    try:
        date_list = start_date.split('/')
        day = int(date_list[0])
        month = int(date_list[1])
        year = int(date_list[2])
        this_time = datetime(year, month, day, 0, 0, tzinfo=timezone.utc)
        this_timestamp = datetime.timestamp(this_time)*1000
        return this_timestamp
    except:
        print("Incorrect format! Try again...")
        pass

# GET VALID FILTER VALUES

def get_valid_guis(swaps_summary):
    valid_guis = []
    for uuid in swaps_summary:
        gui = swaps_summary[uuid]['maker_gui']
        if gui != 'N/A':
            if gui not in valid_guis:
                valid_guis.append(gui)
        gui = swaps_summary[uuid]['taker_gui']
        if gui != 'N/A':
            if gui not in valid_guis:
                valid_guis.append(gui)
    return valid_guis

def get_valid_addresses(swaps_summary):
    valid_addresss = []
    for uuid in swaps_summary:
        address = swaps_summary[uuid]['maker_addr']
        if address != 'N/A':
            if address not in valid_addresss:
                valid_addresss.append(address)
        address = swaps_summary[uuid]['taker_addr']
        if address != 'N/A':
            if address not in valid_addresss:
                valid_addresss.append(address)
    return valid_addresss

def get_valid_versions(swaps_summary):
    valid_versions = []
    for uuid in swaps_summary:
        version = swaps_summary[uuid]['maker_version']
        if version != 'N/A':
            if version not in valid_versions:
                valid_versions.append(version)
        version = swaps_summary[uuid]['taker_version']
        if version != 'N/A':
            if version not in valid_versions:
                valid_versions.append(version)
    return valid_versions

def get_valid_coins(swaps_summary):
    valid_coins = []
    for uuid in swaps_summary:
        coin = swaps_summary[uuid]['maker_coin']
        if coin != 'N/A':
            if coin not in valid_coins:
                valid_coins.append(coin)
        coin = swaps_summary[uuid]['taker_coin']
        if coin != 'N/A':
            if coin not in valid_coins:
                valid_coins.append(coin)
    return valid_coins


# SWAP SUMMARY FILTERS

# by coin
def coin_filter(swaps_summary, coin):
    filtered_swaps_summary = {}
    for uuid in swaps_summary:
        if swaps_summary[uuid]['maker_coin'] == coin or swaps_summary[uuid]['taker_coin'] == coin:
            filtered_swaps_summary.update({uuid:swaps_summary[uuid]})
    return filtered_swaps_summary

def maker_coin_filter(swaps_summary, maker_coin):
    filtered_swaps_summary = {}
    for uuid in swaps_summary:
        if swaps_summary[uuid]['maker_coin'] == maker_coin:
            filtered_swaps_summary.update({uuid:swaps_summary[uuid]})    
    return filtered_swaps_summary

def taker_coin_filter(swaps_summary, taker_coin):
    filtered_swaps_summary = {}
    for uuid in swaps_summary:
        if swaps_summary[uuid]['taker_coin'] == taker_coin:
            filtered_swaps_summary.update({uuid:swaps_summary[uuid]})    
    return filtered_swaps_summary

# by gui
def gui_filter(swaps_summary, gui):
    filtered_swaps_summary = {}
    for uuid in swaps_summary:
        if swaps_summary[uuid]['maker_gui'] == gui or swaps_summary[uuid]['taker_gui'] == gui:
            filtered_swaps_summary.update({uuid:swaps_summary[uuid]})    
    return filtered_swaps_summary

def maker_gui_filter(swaps_summary, maker_gui):
    filtered_swaps_summary = {}
    for uuid in swaps_summary:
        if swaps_summary[uuid]['maker_gui'] == maker_gui:
            filtered_swaps_summary.update({uuid:swaps_summary[uuid]})    
    return filtered_swaps_summary

def taker_gui_filter(swaps_summary, taker_gui):
    filtered_swaps_summary = {}
    for uuid in swaps_summary:
        if swaps_summary[uuid]['taker_gui'] == taker_gui:
            filtered_swaps_summary.update({uuid:swaps_summary[uuid]})    
    return filtered_swaps_summary

# by timestamp range
def time_filter(swaps_summary, from_timestamp, to_timestamp):
    filtered_swaps_summary = {}
    for uuid in swaps_summary:
        swap_finish_time = swaps_summary[uuid]['swap_finish_time']
        if swap_finish_time != "N/A":
            filtered_swaps_summary.update({uuid:swaps_summary[uuid]})
    return filtered_swaps_summary

# by address 
def address_filter(swaps_summary, address):
    filtered_swaps_summary = {}
    for uuid in swaps_summary:
        if swaps_summary[uuid]['maker_addr'] == address or swaps_summary[uuid]['taker_addr'] == address:
            filtered_swaps_summary.update({uuid:swaps_summary[uuid]})    
    return filtered_swaps_summary

def maker_address_filter(swaps_summary, maker_address):
    filtered_swaps_summary = {}

    for uuid in swaps_summary:
        if swaps_summary[uuid]['maker_addr'] == maker_address:
            filtered_swaps_summary.update({uuid:swaps_summary[uuid]})
    return filtered_swaps_summary

def taker_address_filter(swaps_summary, taker_address):
    filtered_swaps_summary = {}
    for uuid in swaps_summary:
        if swaps_summary[uuid]['taker_addr'] == taker_address:
            filtered_swaps_summary.update({uuid:swaps_summary[uuid]})    
    return filtered_swaps_summary

# by version
def version_filter(swaps_summary, version):
    filtered_swaps_summary = {}
    for uuid in swaps_summary:
        if swaps_summary[uuid]['maker_version'] == version or swaps_summary[uuid]['taker_version'] == version:
            filtered_swaps_summary.update({uuid:swaps_summary[uuid]})    
    return filtered_swaps_summary

def maker_version_filter(swaps_summary, maker_version):
    filtered_swaps_summary = {}
    for uuid in swaps_summary:
        if swaps_summary[uuid]['maker_version'] == maker_version:
            filtered_swaps_summary.update({uuid:swaps_summary[uuid]})    
    return filtered_swaps_summary

def taker_version_filter(swaps_summary, taker_version):
    filtered_swaps_summary = {}
    for uuid in swaps_summary:
        if swaps_summary[uuid]['taker_version'] == taker_version:
            filtered_swaps_summary.update({uuid:swaps_summary[uuid]})    
    return filtered_swaps_summary

# by amount
def amount_filter(swaps_summary, amount):
    filtered_swaps_summary = {}
    for uuid in swaps_summary:
        if swaps_summary[uuid]['maker_amount'] == amount or swaps_summary[uuid]['taker_amount'] == amount:
            filtered_swaps_summary.update({uuid:swaps_summary[uuid]})    
    return filtered_swaps_summary

def maker_amount_filter(swaps_summary, maker_amount):
    filtered_swaps_summary = {}
    for uuid in swaps_summary:
        if swaps_summary[uuid]['maker_amount'] == maker_amount:
            filtered_swaps_summary.update({uuid:swaps_summary[uuid]})    
    return filtered_swaps_summary

def taker_amount_filter(swaps_summary, taker_amount):
    filtered_swaps_summary = {}
    for uuid in swaps_summary:
        if swaps_summary[uuid]['taker_amount'] == taker_amount:
            filtered_swaps_summary.update({uuid:swaps_summary[uuid]})    
    return filtered_swaps_summary

# by event
def event_filter(swaps_summary, event, exclude=False):
    filtered_swaps_summary = {}
    for uuid in swaps_summary:
        if exclude:
            if swaps_summary[uuid]['maker_result_event'] != event or swaps_summary[uuid]['taker_result_event'] != event:
                filtered_swaps_summary.update({uuid:swaps_summary[uuid]})    
        else:
            if swaps_summary[uuid]['maker_result_event'] == event or swaps_summary[uuid]['taker_result_event'] == event:
                filtered_swaps_summary.update({uuid:swaps_summary[uuid]})    
    return filtered_swaps_summary

def maker_event_filter(swaps_summary, maker_event, exclude=False):
    filtered_swaps_summary = {}
    for uuid in swaps_summary:
        if exclude:
            if swaps_summary[uuid]['maker_result_event'] != maker_event:
                filtered_swaps_summary.update({uuid:swaps_summary[uuid]})                
        else:
            if swaps_summary[uuid]['maker_result_event'] == maker_event:
                filtered_swaps_summary.update({uuid:swaps_summary[uuid]})    
    return filtered_swaps_summary

def taker_event_filter(swaps_summary, taker_event, exclude=False):
    filtered_swaps_summary = {}
    for uuid in swaps_summary:
        if exclude:
            if swaps_summary[uuid]['taker_result_event'] != taker_event:
                filtered_swaps_summary.update({uuid:swaps_summary[uuid]})    
        else:
            if swaps_summary[uuid]['taker_result_event'] == taker_event:
                filtered_swaps_summary.update({uuid:swaps_summary[uuid]})    
    return filtered_swaps_summary

# by result
def result_filter(swaps_summary, result):
    filtered_swaps_summary = {}
    for uuid in swaps_summary:
        if swaps_summary[uuid]['result'] == result:
            filtered_swaps_summary.update({uuid:swaps_summary[uuid]})    
    return filtered_swaps_summary


# FILE MANAGEMENT
def get_modified_time(file):
    return os.path.getmtime(file)

def write_json(path, filename, data):
    name = filename.split('.')[0]
    jsonfile1 = path+"/"+name+".json"
    jsonfile2 = path+"/"+name+"2.json"
    if not os.path.exists(jsonfile1):
        with open(jsonfile1, "w+") as f:
            f.write('')
    if not os.path.exists(jsonfile2):
        with open(jsonfile2, "w+") as f:
            f.write('')
    if get_modified_time(jsonfile1) < get_modified_time(jsonfile2):
        jsonfile = jsonfile1
    else:
        jsonfile = jsonfile2
    with open(jsonfile, "w+") as f:
        print("Writing "+jsonfile)
        f.write(json.dumps(data))

# assuming start from DB/%NODE_PUBKEY%/SWAPS/STATS/ directory
def fetch_local_maker_files():
    files_content = {}
    files_list_tmp = os.listdir('MAKER')
    files_list = []
    for file in files_list_tmp:
        if file[-5:] == '.json':
            files_list.append(file)
    for file in files_list:
        try:
            with open("MAKER/"+file) as json_file:
                swap_uuid = file[:-5]
                data = json.load(json_file)
                files_content[swap_uuid] = data
        except Exception as e:
            print(e)
            print("Broken: " + file)
    return files_content

# assuming start from DB/%NODE_PUBKEY%/SWAPS/STATS/ directory
def fetch_local_taker_files():
    files_content = {}
    files_list_tmp = os.listdir('TAKER')
    files_list = []
    for file in files_list_tmp:
        if file[-5:] == '.json':
            files_list.append(file)
    for file in files_list:
        try:
            with open("TAKER/"+file) as json_file:
                swap_uuid = file[:-5]
                data = json.load(json_file)
                files_content[swap_uuid] = data
        except Exception as e:
            print(e)
            print("Broken: " + file)
    return files_content

# INFORMATION
def calculate_volumes(swaps_summary, maker_coin, taker_coin):
    filtered_swaps_summary = maker_coin_filter(swaps_summary, maker_coin)
    filtered_swaps_summary = taker_coin_filter(filtered_swaps_summary, taker_coin)
    maker_volume = 0
    taker_volume = 0
    for uuid in filtered_swaps_summary:
        if filtered_swaps_summary[uuid]['maker_amount'] != 'N/A':
            maker_volume += float(filtered_swaps_summary[uuid]['maker_amount'])
        if filtered_swaps_summary[uuid]['taker_amount'] != 'N/A':
            taker_volume += float(filtered_swaps_summary[uuid]['taker_amount'])
    return maker_volume, taker_volume

def calculate_success(swaps_summary):
    success_count = 0
    for uuid in swaps_summary:
        if swaps_summary[uuid]['result'] == 'Success':
            success_count += 1
    return success_count

def calculate_failed(swaps_summary):
    failed_count = 0
    for uuid in swaps_summary:
        if swaps_summary[uuid]['result'] == 'Failed':
            failed_count += 1
    return failed_count

def calculate_total(swaps_summary):
    return len(swaps_summary)

def get_swap_times_list(swaps_summary):
    swap_times = []
    for uuid in swaps_summary:
        if swaps_summary[uuid]['swap_finish_time'] != 'N/A':
            swap_times.append(swaps_summary[uuid]['swap_finish_time'])
    return swap_times

def get_trade_uuid_list(swaps_summary):
    trade_uuids = []
    for uuid in swaps_summary:
        trade_uuids.append(uuid)
    return trade_uuids

def get_guis_list(swaps_summary, role='both'):
    guis_list = []
    if role == 'both':
        guis_list = get_valid_guis(swaps_summary)
    elif role == 'maker':
        for uuid in swaps_summary:
            if swaps_summary[uuid]['maker_gui'] not in guis_list:
                guis_list.append(swaps_summary[uuid]['maker_gui'])
    elif role == 'taker':
        for uuid in swaps_summary:
            if swaps_summary[uuid]['taker_gui'] not in guis_list:
                guis_list.append(swaps_summary[uuid]['taker_gui'])
    return guis_list

def get_versions_list(swaps_summary, role='both'):
    versions_list = []
    if role == 'both':
        versions_list = get_valid_versions(swaps_summary)
    elif role == 'maker':
        for uuid in swaps_summary:
            if swaps_summary[uuid]['maker_version'] not in versions_list:
                versions_list.append(swaps_summary[uuid]['maker_version'])
    elif role == 'taker':
        for uuid in swaps_summary:
            if swaps_summary[uuid]['maker_version'] not in versions_list:
                versions_list.append(swaps_summary[uuid]['taker_version'])
    return versions_list

def address_summary_json(swaps_summary):
    addresses_summary = {}
    known_addresses = get_valid_addresses(swaps_summary)
    for address in known_addresses:
        maker_swaps_summary = maker_address_filter(swaps_summary, address)
        taker_swaps_summary = taker_address_filter(swaps_summary, address)

        successful_maker = calculate_success(maker_swaps_summary)
        failed_maker = calculate_failed(maker_swaps_summary)
        total_maker = calculate_total(maker_swaps_summary)

        successful_taker = calculate_success(taker_swaps_summary)
        failed_taker = calculate_failed(taker_swaps_summary)
        total_taker = calculate_total(taker_swaps_summary)

        successful = successful_maker + successful_taker
        failed = failed_maker + failed_taker
        total = total_maker + total_taker

        maker_swap_times = get_swap_times_list(maker_swaps_summary)
        if len(maker_swap_times) > 0:
            first_swap_maker = min(maker_swap_times)
            last_swap_maker = max(maker_swap_times)
        else:
            first_swap_maker = "N/A"
            last_swap_maker = "N/A"

        taker_swap_times = get_swap_times_list(taker_swaps_summary)
        if len(taker_swap_times) > 0:
            first_swap_taker = min(taker_swap_times)
            last_swap_taker = max(taker_swap_times)
        else:
            first_swap_taker = "N/A"
            last_swap_taker = "N/A"

        all_swap_times = maker_swap_times + taker_swap_times
        if len(all_swap_times) > 0:
            first_swap = min(all_swap_times)
            last_swap = max(all_swap_times)
        else:
            first_swap = "N/A"
            last_swap = "N/A"
       
        maker_trades = get_trade_uuid_list(maker_swaps_summary)
        taker_trades = get_trade_uuid_list(taker_swaps_summary)

        maker_guis_used = get_guis_list(maker_swaps_summary, 'maker')
        taker_guis_used = get_guis_list(taker_swaps_summary, 'taker')
        guis_used = list(set(maker_guis_used + taker_guis_used))

        maker_versions_used = get_versions_list(maker_swaps_summary, 'maker')
        taker_versions_used = get_versions_list(taker_swaps_summary, 'taker')
        versions_used = list(set(maker_versions_used + taker_versions_used))


        # TODO: add function for getting volumes data
        this_addr = {
            address:{
                "successful_taker":successful_taker,
                "failed_taker":failed_taker,
                "total_taker":total_taker,
                "successful_maker":successful_maker,
                "failed_maker":failed_maker,
                "total_maker":total_maker,
                "successful":successful,
                "failed":failed,
                "total":total,
                "first_swap_taker":first_swap_taker,
                "last_swap_taker":last_swap_taker,
                "first_swap_maker":first_swap_maker,
                "last_swap_maker":last_swap_maker,
                "first_swap":first_swap,
                "last_swap":last_swap,
                "taker_trades":taker_trades,
                "maker_trades":maker_trades,
                "guis_used":guis_used,
                "versions_used":versions_used,
                "taker_volumes":{},
                "maker_volumes":{}
            }
        }
        addresses_summary.update(this_addr)
    return addresses_summary

# Scan and summarise local maker/taker files
def swaps_summary_json():
    all_maker_data = fetch_local_maker_files()
    all_taker_data = fetch_local_taker_files()
    swaps_summary = {}

    # get maker summary for all maker files
    for uuid in all_maker_data:
        this_swap = {
                uuid:{
                    "maker_coin":"N/A",
                    "taker_coin":"N/A",
                    "maker_addr":"N/A",
                    "taker_addr":"N/A",
                    "maker_amount":"N/A",
                    "taker_amount":"N/A",
                    "maker_gui":"no data",
                    "taker_gui":"no data",
                    "maker_version":"no data",
                    "taker_version":"no data",
                    "maker_errors":[],
                    "taker_errors":[],
                    "maker_finish_time":"N/A",
                    "taker_finish_time":"N/A",
                    "swap_finish_time":"N/A",
                    "maker_result_event":"N/A",
                    "taker_result_event":"N/A",
                    "result":"Success"
                }
            }
        debug_print(colorize(all_maker_data[uuid], 'yellow'), debug)

        failed = False
        if 'gui' in all_maker_data[uuid]:
            this_swap[uuid]['maker_gui'] = all_maker_data[uuid]['gui']
        if 'mm_version' in all_maker_data[uuid]:
            this_swap[uuid]['maker_version'] = all_maker_data[uuid]['mm_version']
        for events in all_maker_data[uuid]['events']:
            if 'data' in events['event']:
                if 'error' in events['event']['data']:
                    this_swap[uuid]['maker_errors'].append(events['event']['data']['error'])
            if events['event']['type'] in maker_errors_events:
                this_swap[uuid]['maker_result_event'] = events['event']['type']
                this_swap[uuid]['result'] = "Failed"
                failed = True
            if events['event']['type'] == 'Started':
                this_swap[uuid]['maker_coin'] = events['event']['data']['maker_coin']
                this_swap[uuid]['taker_coin'] = events['event']['data']['taker_coin']
                this_swap[uuid]['maker_amount'] = events['event']['data']['maker_amount']
                this_swap[uuid]['taker_amount'] = events['event']['data']['taker_amount']
                this_swap[uuid]['maker_addr'] = get_radd_from_pub(events['event']['data']['my_persistent_pub'])
            if events['event']['type'] == 'Negotiated':
                this_swap[uuid]['taker_addr'] = get_radd_from_pub(events['event']['data']['taker_pubkey'])
            if events['event']['type'] == 'Finished':
                this_swap[uuid]['maker_finish_time'] = events['timestamp']
                this_swap[uuid]['swap_finish_time'] = events['timestamp']
            if not failed and events['event']['type'] != 'Finished':
                this_swap[uuid]['maker_result_event'] = events['event']['type']
        
        # add taker info for matching uuid if availble in taker files
        if uuid in all_taker_data:
            debug_print(colorize(all_taker_data[uuid], 'blue'), debug)
            failed = False
            for events in all_taker_data[uuid]['events']:
                if 'gui' in all_taker_data[uuid]:
                    this_swap[uuid]['taker_gui'] = all_taker_data[uuid]['gui']
                if 'mm_version' in all_taker_data[uuid]:
                    this_swap[uuid]['taker_version'] = all_taker_data[uuid]['mm_version']
                if events['event']['type'] == 'Finished':
                    this_swap[uuid]['taker_finish_time'] = events['timestamp']
                if 'data' in events['event']:
                    if 'error' in events['event']['data']:
                        this_swap[uuid]['taker_errors'].append(events['event']['data']['error'])
                if events['event']['type'] in taker_errors_events:
                    this_swap[uuid]['taker_result_event'] = events['event']['type']
                    this_swap[uuid]['result'] = "Failed"
                    failed = True
                if events['event']['type'] == 'Started':
                    if this_swap[uuid]['maker_coin'] == 'N/A':
                        this_swap[uuid]['maker_coin'] = events['event']['data']['maker_coin']
                    if this_swap[uuid]['taker_coin'] == 'N/A':
                        this_swap[uuid]['taker_coin'] = events['event']['data']['taker_coin']
                    if this_swap[uuid]['maker_amount'] == 'N/A':
                        this_swap[uuid]['maker_amount'] = events['event']['data']['maker_amount']
                    if this_swap[uuid]['taker_amount'] == 'N/A':
                        this_swap[uuid]['taker_amount'] = events['event']['data']['taker_amount']
                    if this_swap[uuid]['taker_addr'] == 'N/A':
                        this_swap[uuid]['taker_addr'] = get_radd_from_pub(events['event']['data']['my_persistent_pub'])
                if events['event']['type'] == 'Negotiated':
                    if this_swap[uuid]['maker_addr'] == 'N/A':
                        this_swap[uuid]['maker_addr'] = get_radd_from_pub(events['event']['data']['maker_pubkey'])
                if events['event']['type'] == 'Finished':
                    this_swap[uuid]['taker_finish_time'] = events['timestamp']
                if not failed and events['event']['type'] != 'Finished':
                    this_swap[uuid]['taker_result_event'] = events['event']['type']
                if this_swap[uuid]['swap_finish_time'] == 'N/A':
                    this_swap[uuid]['swap_finish_time'] = events['timestamp']
                elif this_swap[uuid]['swap_finish_time'] < events['timestamp']:
                    this_swap[uuid]['swap_finish_time'] = events['timestamp']

        if len(this_swap[uuid]['maker_errors']) == 0:
            if len(this_swap[uuid]['maker_errors']) == 0:
                msg = colorize(this_swap[uuid], 'green')
            else:
                msg = colorize(this_swap[uuid], 'lightred')
        else:
            msg = colorize(this_swap[uuid], 'red')
        debug_print(msg, debug)
        swaps_summary.update(this_swap)

    # Get taker summary if uuid not found in maker files
    for uuid in all_taker_data:
        if uuid not in swaps_summary:
            this_swap = {
                    uuid:{
                        "maker_coin":"N/A",
                        "taker_coin":"N/A",
                        "maker_addr":"N/A",
                        "taker_addr":"N/A",
                        "maker_amount":"N/A",
                        "taker_amount":"N/A",
                        "maker_gui":"no data",
                        "taker_gui":"no data",
                        "maker_version":"no data",
                        "taker_version":"no data",
                        "maker_errors":[],
                        "taker_errors":[],
                        "maker_finish_time":"N/A",
                        "taker_finish_time":"N/A",
                        "swap_finish_time":"N/A",
                        "maker_result_event":"N/A",
                        "taker_result_event":"N/A",
                        "result":"Success"
                    }
                }
            debug_print(colorize(all_taker_data[uuid], 'blue'), debug)
            failed = False
            if 'gui' in all_taker_data[uuid]:
                this_swap[uuid]['taker_gui'] = all_taker_data[uuid]['gui']
            if 'mm_version' in all_taker_data[uuid]:
                this_swap[uuid]['taker_version'] = all_taker_data[uuid]['mm_version']
            for events in all_taker_data[uuid]['events']:
                if 'data' in events['event']:
                    if 'error' in events['event']['data']:
                        this_swap[uuid]['taker_errors'].append(events['event']['data']['error'])
                if events['event']['type'] in taker_errors_events:
                    this_swap[uuid]['taker_result_event'] = events['event']['type']
                    this_swap[uuid]['result'] = "Failed"
                    failed = True
                if events['event']['type'] == 'Started':
                    this_swap[uuid]['maker_coin'] = events['event']['data']['maker_coin']
                    this_swap[uuid]['taker_coin'] = events['event']['data']['taker_coin']
                    this_swap[uuid]['maker_amount'] = events['event']['data']['maker_amount']
                    this_swap[uuid]['taker_amount'] = events['event']['data']['taker_amount']
                    this_swap[uuid]['taker_addr'] = get_radd_from_pub(events['event']['data']['my_persistent_pub'])
                if events['event']['type'] == 'Negotiated':
                    this_swap[uuid]['maker_addr'] = get_radd_from_pub(events['event']['data']['maker_pubkey'])
                if events['event']['type'] == 'Finished':
                    this_swap[uuid]['taker_finish_time'] = events['timestamp']
                    this_swap[uuid]['swap_finish_time'] = events['timestamp']
                if not failed and events['event']['type'] != 'Finished':
                    this_swap[uuid]['taker_result_event'] = events['event']['type']
            if len(this_swap[uuid]['maker_errors']) == 0:
                if len(this_swap[uuid]['taker_errors']) == 0:
                    msg = colorize(this_swap[uuid], 'green')
                else:
                    msg = colorize(this_swap[uuid], 'lightred')
            else:
                msg = colorize(this_swap[uuid], 'red')
            debug_print(msg, debug)
            swaps_summary.update(this_swap)

    # once complete, run through for missing maker / taker addr, try pubkey prefixes and select if 02/03 matches known address in other uuid.
    known_addresses = get_valid_addresses(swaps_summary)

    for uuid in swaps_summary:
        if swaps_summary[uuid]['maker_addr'] == 'N/A':
            if uuid in all_taker_data:
                for events in all_taker_data[uuid]['events']:
                    if events['event']['type'] == "Started":
                        maker_pub = events['event']['data']['maker']
                        addr = get_radd_from_pub("02"+maker_pub)
                        if addr not in known_addresses:
                            addr = get_radd_from_pub("03"+maker_pub)
                        if addr not in known_addresses:
                            addr = 'Insufficient data' # maybe can check block explorer?
                        swaps_summary[uuid]['maker_addr'] == addr
        if swaps_summary[uuid]['taker_addr'] == 'N/A':
            if uuid in all_maker_data:
                for events in all_maker_data[uuid]['events']:
                    if events['event']['type'] == "Started":
                        taker_pub = events['event']['data']['taker']
                        addr = get_radd_from_pub("02"+taker_pub)
                        if addr not in known_addresses:
                            addr = get_radd_from_pub("03"+taker_pub)
                        if addr not in known_addresses:
                            addr = 'Insufficient data' # maybe can check block explorer?
                        swaps_summary[uuid]['taker_addr'] == addr
    return swaps_summary
