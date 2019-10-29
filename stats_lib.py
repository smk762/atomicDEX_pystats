#!/usr/bin/env python3
import os
import json
import bitcoin
from bitcoin.wallet import P2PKHBitcoinAddress
from bitcoin.core import x
from bitcoin.core import CoreMainParams

class CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 60,
                       'SCRIPT_ADDR': 85,
                       'SECRET_KEY': 188}
bitcoin.params = CoinParams

def get_radd_from_pub(pub):
    try:
        taker_addr = str(P2PKHBitcoinAddress.from_pubkey(x("02"+pub)))
    except:
        taker_addr = pub
    return str(taker_addr)

error_events = [
    # ignoring early fail events as swap not yet started
    #"StartFailed",
    #"NegotiateFailed",
    "TakerFeeValidateFailed",
    "MakerPaymentTransactionFailed",
    "MakerPaymentDataSendFailed",
    "TakerPaymentValidateFailed",
    "TakerPaymentSpendFailed",
    "MakerPaymentRefunded",
    "MakerPaymentRefundFailed"
  ]
ignore_events = [
    "StartFailed",
    "NegotiateFailed",
    ]


# assuming start from DB/%NODE_PUBKEY%/SWAPS/STATS/ directory
# TODO TAKER folder?
def fetch_local_swap_files():
    files_content = {}
    files_list_tmp = os.listdir('MAKER')
    files_list = []
    for file in files_list_tmp:
        if file[-5:] == '.json':
            files_list.append(file)

    # loading files content into files_content dict
    for file in files_list:
        try:
            with open('MAKER'+"/"+file) as json_file:
                swap_uuid = file[:-5]
                data = json.load(json_file)
                files_content[swap_uuid] = data
        except Exception as e:
            print(e)
            print("Broken: " + file)
    return files_content


# filter swaps data for speciifc pair
def pair_filter(data_to_filter, maker_coin, taker_coin):
    swaps_of_pair = {}
    for swap_data in data_to_filter.values():
        try:
            if taker_coin == 'All':
                if swap_data["events"][0]["event"]["data"]["maker_coin"] == maker_coin:
                    swaps_of_pair[swap_data["events"][0]["event"]["data"]["uuid"]] = swap_data
            elif maker_coin == 'All':
                if swap_data["events"][0]["event"]["data"]["taker_coin"] == taker_coin:
                    swaps_of_pair[swap_data["events"][0]["event"]["data"]["uuid"]] = swap_data
            else:
                if swap_data["events"][0]["event"]["data"]["taker_coin"] == taker_coin and swap_data["events"][0]["event"]["data"]["maker_coin"] == maker_coin:
                    swaps_of_pair[swap_data["events"][0]["event"]["data"]["uuid"]] = swap_data
        except Exception as e:
            #print(e)
            pass
    return swaps_of_pair

# filter swaps data for specific gui
def gui_filter(data_to_filter, gui_type):
    gui_types = []
    swaps_of_gui = {}
    for swap_data in data_to_filter.values():
        if 'gui' in swap_data:
            gui = str(swap_data['gui'])
        else:
            gui = "Not Specified"
        if gui not in gui_types:
            gui_types.append(gui)
        try:
            if gui_type == gui:
                swaps_of_gui[swap_data["events"][0]["event"]["data"]["uuid"]] = swap_data
        except Exception as e:
            #print(e)
            pass
    return swaps_of_gui, gui_types


# filter for time period
def time_filter(data_to_filter, start_time_stamp, end_time_stamp):
    swaps_for_dates = {}
    for swap_data in data_to_filter.values():
        try:
            if swap_data["events"][0]["timestamp"] >= start_time_stamp and swap_data["events"][0]["timestamp"] <= end_time_stamp:
                swaps_for_dates[swap_data["events"][0]["event"]["data"]["uuid"]] = swap_data
        except Exception as e:
            pass
    return swaps_for_dates



ignored_addresses = ['RDbAXLCmQ2EN7daEZZp7CC9xzkcN8DfAZd', '']

# checking if swap succesfull
def count_successful_swaps(swaps_data, from_timestamp=0, to_timestamp=999999999999999):
    failed_events_data = {}
    gui_types = {}
    gui_types['Not Specified'] = {}
    gui_types['Not Specified']['failed'] = 0
    gui_types['Not Specified']['successful'] = 0
    successful_swaps_counter = 0
    failed_swaps_counter = 0
    taker_addresses = {}
    for swap_data in swaps_data.values():
        if 'gui' in swap_data:
            gui_type = str(swap_data['gui'])
        else:
            gui_type = "Not Specified"
        if gui_type not in gui_types:
            gui_types[gui_type] = {}
            gui_types[gui_type]['failed'] = 0
            gui_types[gui_type]['successful'] = 0
        failed = False
        ignore_swap = False
        taker_addr = ''
        swap_time_include = True
        for event in swap_data["events"]:
            if event['event']['type'] in ignore_events:
                ignore_swap = True
        if not ignore_swap:
            for event in swap_data["events"]:
                if event['event']['type'] == 'Started':
                    if event['timestamp'] < from_timestamp or event['timestamp'] > to_timestamp:
                        swap_time_include = False
                        break
                    taker_pub = event['event']['data']['taker']
                    taker_addr = get_radd_from_pub(taker_pub)
                    if taker_addr in ignored_addresses:
                        break
                    if taker_addr not in taker_addresses:
                        taker_addresses[taker_addr] = {}
                        taker_addresses[taker_addr]['failed'] = 0
                        taker_addresses[taker_addr]['successful'] = 0
                        taker_addresses[taker_addr]['last_swap'] = event['timestamp']
                    elif taker_addresses[taker_addr]['last_swap'] < event['timestamp']:
                        taker_addresses[taker_addr]['last_swap'] = event['timestamp']
                if event["event"]["type"] in error_events:
                    failed = True
                    failed_events_data[swap_data["uuid"]] = {}
                    failed_events_data[swap_data["uuid"]]["date"] = event["timestamp"]
                    try:
                        failed_events_data[swap_data["uuid"]]["taker_coin"] = swap_data["events"][0]["event"]["data"]["taker_coin"]
                        failed_events_data[swap_data["uuid"]]["maker_coin"] = swap_data["events"][0]["event"]["data"]["maker_coin"]
                    except Exception as e:
                        failed_events_data[swap_data["uuid"]]["taker_coin"] = "N/A"
                        failed_events_data[swap_data["uuid"]]["make_coin"] = "N/A"
                    finally:
                        failed_events_data[swap_data["uuid"]]["maker_fail_event_type"] = event["event"]["type"]
                        failed_events_data[swap_data["uuid"]]["maker_error"] = event["event"]["data"]["error"]
                    break
            if failed:
                gui_types[gui_type]['failed'] += 1
            else:
                gui_types[gui_type]['successful'] += 1
            if taker_addr not in ignored_addresses:
                if swap_time_include:
                    if failed:
                        taker_addresses[taker_addr]['failed'] += 1
                        failed_swaps_counter += 1
                    else:
                        successful_swaps_counter += 1
                        taker_addresses[taker_addr]['successful'] += 1
    for taker_addr in taker_addresses:
        taker_addresses[taker_addr]['total'] = taker_addresses[taker_addr]['failed'] + taker_addresses[taker_addr]['successful']
    return [failed_swaps_counter, successful_swaps_counter, failed_events_data, taker_addresses, gui_types]


# calculate volumes, assumes filtered data for pair
def calculate_trades_volumes(swaps_data):
    maker_coin_volume = 0
    taker_coin_volume = 0
    for swap_data in swaps_data.values():
        try:
            maker_coin_volume += float(swap_data["events"][0]["event"]["data"]["maker_amount"])
            taker_coin_volume += float(swap_data["events"][0]["event"]["data"]["taker_amount"])
        except Exception as e:
            print(swap_data["events"][0])
            print(e)
    return (maker_coin_volume, taker_coin_volume)
