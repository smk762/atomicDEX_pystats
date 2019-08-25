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

# assuming start from DB/%NODE_PUBKEY%/SWAPS/STATS/ directory
def fetch_local_swap_files():
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
    successful_swaps_counter = 0
    failed_swaps_counter = 0
    for swap_data in swaps_data.values():
        for event in swap_data["events"]:
            if event["event"]["type"] in error_events:
                failed_swaps_counter += 1
            else:
                successful_swaps_counter += 1
    return (failed_swaps_counter, successful_swaps_counter)

# calculate volumes
# TODO: ETH/ERC volumes seems not possible to calculate this way
def calculate_trades_volumes(swaps_data):
    maker_coin_volume = 0
    taker_coin_volume = 0
    for swap_data in swaps_data.values():
        for event in swap_data["events"]:
            if event["event"]["type"] == "MakerPaymentSent":
                maker_coin_volume += abs(event["event"]["data"]["my_balance_change"])
            elif event["event"]["type"] == "TakerPaymentSpent":
                taker_coin_volume += abs(event["event"]["data"]["my_balance_change"])
    return (maker_coin_volume, taker_coin_volume)
