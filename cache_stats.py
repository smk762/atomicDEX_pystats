#!/usr/bin/env python3
import os
import sys
import json
import stats_lib
import requests
from datetime import datetime, timezone
from os.path import expanduser


# Get and set config
cwd = os.getcwd()
home = expanduser("~")
now = datetime.now()
timestamp_now = datetime.timestamp(now)

maker_error_events_count = {
    #"StartFailed": 0,
    #"NegotiateFailed": 0,
    "TakerFeeValidateFailed": 0,
    "MakerPaymentTransactionFailed": 0,
    "MakerPaymentDataSendFailed": 0,
    "TakerPaymentValidateFailed": 0,
    "TakerPaymentSpendFailed": 0,
    "MakerPaymentRefunded": 0,
    "MakerPaymentRefundFailed": 0
}

json_path = '/var/www/html/json'
#start_timestamp = 1572523200000
start_timestamp = 1572350400000
end_timestamp = int(timestamp_now)*1000

data = stats_lib.fetch_local_swap_files()
raw_data = stats_lib.count_successful_swaps(data, start_timestamp, end_timestamp)
failed_events_data = raw_data[2]
taker_addresses = raw_data[3]
if len(taker_addresses) > 0:
    if len(failed_events_data) > 0:
        stats_lib.write_json(json_path, 'All--All--fail_events.json', failed_events_data)
    stats_lib.write_json(json_path, 'All--All--addresses.json', taker_addresses)
    stats_lib.write_json(json_path, 'All--All--raw_data.json', raw_data)
    swap_json = {
        "result": "success",
        "taker" : 'All',
        "maker" : 'All',
        "time_now" : int(timestamp_now)*1000,
        "total": raw_data[1] + raw_data[0],
        "successful": raw_data[1],
        "failed": raw_data[0]
    }
    swap_json.update({"from_timestamp": int(start_timestamp)})
    swap_json.update({"to_timestamp": int(end_timestamp)})
    swap_json.update({"gui_filter": 'All'})
    if raw_data[1]+raw_data[0] > 0:
        pct = round(raw_data[1]/(raw_data[1]+raw_data[0])*100, 2)
        swap_json.update({"success_rate": str(pct)+"%"})
    stats_lib.write_json(json_path, "All--All--swapstats.json", swap_json)

for maker in stats_lib.valid_tickers:
    taker = 'All'
    pair = maker+"-"+taker
    raw_pair_data = stats_lib.pair_filter(data, maker, taker)
    pair_data = stats_lib.count_successful_swaps(raw_pair_data, start_timestamp, end_timestamp)
    failed_events_data = pair_data[2]
    taker_addresses = pair_data[3]
    if len(taker_addresses) > 0:
        if len(failed_events_data) > 0:
            stats_lib.write_json(json_path, pair+'--All--fail_events.json', failed_events_data)
        stats_lib.write_json(json_path, pair+'--All--raw_data.json', pair_data)
        stats_lib.write_json(json_path, pair+'--All--addresses.json', taker_addresses)
        swap_json = {
            "result": "success",
            "taker" : taker,
            "maker" : maker,
            "time_now" : int(timestamp_now)*1000,
            "total": pair_data[1] + pair_data[0],
            "successful": pair_data[1],
            "failed": pair_data[0]
        }
        swap_json.update({"from_timestamp": int(start_timestamp)})
        swap_json.update({"to_timestamp": int(end_timestamp)})
        swap_json.update({"gui_filter": 'All'})
        if pair_data[1]+pair_data[0] > 0:
            pct = round(pair_data[1]/(pair_data[1]+pair_data[0])*100, 2)
            swap_json.update({"success_rate": str(pct)+"%"})
        stats_lib.write_json(json_path, pair+"--All--swapstats.json", swap_json)
    for gui_type in stats_lib.valid_guis:
        gui_name = gui_type.replace(" ","_")
        gui_name = gui_name.replace(".","_")
        raw_gui_data = stats_lib.gui_filter(raw_pair_data, gui_type)
        gui_data = stats_lib.count_successful_swaps(raw_gui_data, start_timestamp, end_timestamp)
        failed_events_data = gui_data[2]
        taker_addresses = gui_data[3]
        if len(taker_addresses) > 0:
            if len(failed_events_data) > 0:
                stats_lib.write_json(json_path, pair+"--"+gui_name+'--fail_events.json', failed_events_data)
            stats_lib.write_json(json_path, pair+"--"+gui_name+'--raw_data.json', gui_data)
            stats_lib.write_json(json_path, pair+"--"+gui_name+'--addresses.json', taker_addresses)
            swap_json = {
                "result": "success",
                "taker" : taker,
                "maker" : maker,
                "time_now" : int(timestamp_now)*1000,
                "total": gui_data[1] + gui_data[0],
                "successful": gui_data[1],
                "failed": gui_data[0]
            }
            swap_json.update({"from_timestamp": int(start_timestamp)})
            swap_json.update({"to_timestamp": int(end_timestamp)})
            swap_json.update({"gui_filter": gui_type})
            if gui_data[1]+gui_data[0] > 0:
                pct = round(gui_data[1]/(gui_data[1]+gui_data[0])*100, 2)
                swap_json.update({"success_rate": str(pct)+"%"})
            stats_lib.write_json(json_path, pair+"--"+gui_name+"--swapstats.json", swap_json)

    for taker in stats_lib.valid_tickers:
        if maker != taker:
            pair = maker+"-"+taker
            raw_pair_data = stats_lib.pair_filter(data, maker, taker)
            pair_data = stats_lib.count_successful_swaps(raw_pair_data, start_timestamp, end_timestamp)
            failed_events_data = pair_data[2]
            taker_addresses = pair_data[3]
            if len(taker_addresses) > 0:
                if len(failed_events_data) > 0:
                    stats_lib.write_json(json_path, pair+'--All--fail_events.json', failed_events_data)
                stats_lib.write_json(json_path, pair+'--All--raw_data.json', pair_data)
                stats_lib.write_json(json_path, pair+'--All--addresses.json', taker_addresses)
                swap_json = {
                    "result": "success",
                    "taker" : taker,
                    "maker" : maker,
                    "time_now" : int(timestamp_now)*1000,
                    "total": pair_data[1] + pair_data[0],
                    "successful": pair_data[1],
                    "failed": pair_data[0]
                }
                swap_json.update({"from_timestamp": int(start_timestamp)})
                swap_json.update({"to_timestamp": int(end_timestamp)})
                swap_json.update({"gui_filter": 'All'})
                if pair_data[1]+pair_data[0] > 0:
                    pct = round(pair_data[1]/(pair_data[1]+pair_data[0])*100, 2)
                    swap_json.update({"success_rate": str(pct)+"%"})
                stats_lib.write_json(json_path, pair+"--All--swapstats.json", swap_json)

            for gui_type in stats_lib.valid_guis:
                gui_name = gui_type.replace(" ","_")
                gui_name = gui_name.replace(".","_")
                raw_gui_data = stats_lib.gui_filter(raw_pair_data, gui_type)
                gui_data = stats_lib.count_successful_swaps(raw_gui_data, start_timestamp, end_timestamp)
                failed_events_data = gui_data[2]
                taker_addresses = gui_data[3]
                if len(taker_addresses) > 0:
                    if len(failed_events_data) > 0:
                        stats_lib.write_json(json_path, pair+"--"+gui_name+'--fail_events.json', failed_events_data)
                    stats_lib.write_json(json_path, pair+"--"+gui_name+'--raw_data.json', gui_data)
                    stats_lib.write_json(json_path, pair+"--"+gui_name+'--addresses.json', taker_addresses)
                    swap_json = {
                        "result": "success",
                        "taker" : taker,
                        "maker" : maker,
                        "time_now" : int(timestamp_now)*1000,
                        "total": gui_data[1] + gui_data[0],
                        "successful": gui_data[1],
                        "failed": gui_data[0]
                    }
                    swap_json.update({"from_timestamp": int(start_timestamp)})
                    swap_json.update({"to_timestamp": int(end_timestamp)})
                    swap_json.update({"gui_filter": gui_type})
                    if gui_data[1]+gui_data[0] > 0:
                        pct = round(gui_data[1]/(gui_data[1]+gui_data[0])*100, 2)
                        swap_json.update({"success_rate": str(pct)+"%"})
                    stats_lib.write_json(json_path, pair+"--"+gui_name+"--swapstats.json", swap_json)


for gui_type in stats_lib.valid_guis:
    gui_name = gui_type.replace(" ","_")
    gui_name = gui_name.replace(".","_")
    raw_gui_data = stats_lib.gui_filter(data, gui_type)
    gui_data = stats_lib.count_successful_swaps(raw_gui_data, start_timestamp, end_timestamp)
    failed_events_data = gui_data[2]
    taker_addresses = gui_data[3]
    if len(taker_addresses) > 0:
        if len(failed_events_data) > 0:
            stats_lib.write_json(json_path, "All--"+gui_name+'--fail_events.json', failed_events_data)
        stats_lib.write_json(json_path, "All--"+gui_name+'--addresses.json', taker_addresses)
        stats_lib.write_json(json_path, "All--"+gui_name+'--raw_data.json', gui_data)
        swap_json = {
            "result": "success",
            "taker" : 'All',
            "maker" : 'All',
            "time_now" : int(timestamp_now)*1000,
            "total": gui_data[1] + gui_data[0],
            "successful": gui_data[1],
            "failed": gui_data[0]
        }
        swap_json.update({"from_timestamp": int(start_timestamp)})
        swap_json.update({"to_timestamp": int(end_timestamp)})
        swap_json.update({"gui_filter": gui_type})
        if gui_data[1]+gui_data[0] > 0:
            pct = round(gui_data[1]/(gui_data[1]+gui_data[0])*100, 2)
            swap_json.update({"success_rate": str(pct)+"%"})
        stats_lib.write_json(json_path, "All--"+gui_name+"--swapstats.json", swap_json)


