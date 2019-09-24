import os
import json

error_events = [
    "StartFailed",
    "NegotiateFailed",
    "TakerFeeValidateFailed",
    "MakerPaymentTransactionFailed",
    "MakerPaymentDataSendFailed",
    "TakerPaymentValidateFailed",
    "TakerPaymentSpendFailed",
    "MakerPaymentRefunded",
    "MakerPaymentRefundFailed"
  ]

stats_folder = "enter path to stats folder here"
# e.g. "/home/username/mm2/DB/node_pubkey/SWAPS/STATS/"

def fetch_local_swap_files():
    try:
        os.chdir(stats_folder)
    except:
        print("Folder ("+stats_folder+") not found! Confirm correct path set in stats_lib.py")
        exit(0)
    files_list_tmp = os.listdir("MAKER")
    files_list = []
    for file in files_list_tmp:
        if file[-5:] == '.json':
            files_list.append(file)

    files_content = {}

    # loading files content into files_content dict
    for file in files_list:
        try:
            with open('MAKER/'+file) as json_file:
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
            if swap_data["events"][0]["event"]["data"]["taker_coin"] == taker_coin and swap_data["events"][0]["event"]["data"]["maker_coin"] == maker_coin:
                swaps_of_pair[swap_data["events"][0]["event"]["data"]["uuid"]] = swap_data
        except Exception:
            pass
    return swaps_of_pair

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


# checking if swap succesfull
def count_successful_swaps(swaps_data):
    fails_info = []
    error_type_counts = {}
    for event in error_events:
        error_type_counts[event] = 0
    successful_swaps_counter = 0
    failed_swaps_counter = 0
    for swap_data in swaps_data.values():
        failed = False
        for event in swap_data["events"]:
            if event["event"]["type"] in error_events:
                error_type_counts[event["event"]["type"]] += 1
                taker_coin = swap_data["events"][0]['event']['data']['taker_coin']
                maker_coin = swap_data["events"][0]['event']['data']['maker_coin']
                taker_pub = swap_data["events"][0]['event']['data']['taker']
                fail_uuid = swap_data['uuid']
                fail_timestamp = event['timestamp']
                fail_error = event["event"]["data"]['error']
                fail_data = {
                    "uuid": fail_uuid,
                    "fail_event": event["event"]["type"],
                    "time": fail_timestamp,
                    "pair": taker_coin+" - "+maker_coin,
                    "taker_pub": taker_pub,
                    "error": fail_error
                }
                fails_info.append(fail_data)
                failed = True
                break
        if failed:
            failed_swaps_counter += 1
        else:
            successful_swaps_counter += 1
    return (failed_swaps_counter, successful_swaps_counter, error_type_counts, fails_info)

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
