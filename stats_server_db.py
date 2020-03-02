#!/usr/bin/env python3from typing import Optional, List
from fastapi import Depends, FastAPI, HTTPException
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
#from pydantic import BaseModel, Field
from starlette.status import HTTP_401_UNAUTHORIZED
from threading import Thread
from lib import stats_lib, dblib
from datetime import datetime, timezone
import uvicorn 
import logging
import logging.handlers

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

app = FastAPI()

now = datetime.now()
timestamp_now = datetime.timestamp(now)

@app.get('/')
async def home():
    return {
        "result":"success",
        "message": "Welcome to AtomicDEX Stats Prototype API for AtomicDEX stats v0.0.3. See /docs for all methods"
    }

@app.get('/atomicstats/api/fail_count')
async def fail_count(taker_coin: str=None, maker_coin: str=None, mins_since: int=None):
    resp = dblib.get_failed(maker_coin, taker_coin, mins_since)
    return {
        "result":"success",
        "message": resp
    }

# optional: pair, dates
@app.get('/atomicstats/api/v1.0/get_success_rate')
async def get_volumes():
    error_msg = ''
    maker = 'All'
    taker = 'All'
    query_parameters = request.args
    print(query_parameters)
    if "from" in query_parameters:
        from_timestamp = request.args["from"]
    else:
        from_timestamp = '0000000000000'
    if "to" in query_parameters:
        to_timestamp = request.args["to"]
    else:
        to_timestamp = '9999999999999'
    if (len(from_timestamp) != 13) or (len(to_timestamp) != 13):
        error_msg += "Please use miliseconds 13 digits timestamp! "
    if int(from_timestamp) > int(to_timestamp):
        error_msg += "From timestamp should be before to timestamp! "
    if "taker" in query_parameters:
        taker = request.args["taker"]
        if taker not in stats_lib.valid_tickers:
            error_msg += "taker ["+taker+"] is an invalid ticker! Available options are "+str(stats_lib.valid_tickers)+". "
    if "maker" in query_parameters:
        maker = request.args["maker"]
        if maker not in stats_lib.valid_tickers:
            error_msg += "maker ["+maker+"] is an invalid ticker! Available options are "+str(stats_lib.valid_tickers)+". "
    swap_data = stats_lib.fetch_local_swap_files()
    if "gui" in query_parameters:
        swap_data = stats_lib.gui_filter(swap_data, request.args["gui"])
        if request.args["gui"] not in stats_lib.valid_guis:
            error_msg += "GUI ["+request.args['gui']+"] is invalid! Available options are "+str(stats_lib.valid_guis)+". "
    if maker != 'All' or taker != 'All':
        swap_data = stats_lib.pair_filter(swap_data, maker, taker)
    success_rate = stats_lib.count_successful_swaps(swap_data, int(from_timestamp), int(to_timestamp))
    if error_msg != '':
        data = {
        "result" : "error",
        "error" : error_msg
        }
    else:
        data = {
        "result": "success",
        "maker" : maker,
        "taker" : taker,
        "time_now" : int(timestamp_now)*1000,
        "total": success_rate[1] + success_rate[0],
        "successful": success_rate[1],
        "failed": success_rate[0]

        }
        if from_timestamp != '0000000000000':
            data.update({"from_timestamp": int(from_timestamp)})
        if to_timestamp != '9999999999999':
            data.update({"to_timestamp": int(to_timestamp)})
        if "gui" in query_parameters:
            data.update({"gui_filter": request.args['gui']})
        if success_rate[1]+success_rate[0] > 0:
            pct = round(success_rate[1]/(success_rate[1]+success_rate[0])*100, 2)
            data.update({"success_rate": str(pct)+"%"})
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

@app.get('/atomicstats/api/v1.0/get_fail_data')
async def get_fails():
    error_msg = ''
    maker = 'All'
    taker = 'All'
    query_parameters = request.args
    if "from" in query_parameters:
        from_timestamp = request.args["from"]
    else:
        from_timestamp = '0000000000000'
    if "to" in query_parameters:
        to_timestamp = request.args["to"]
    else:
        to_timestamp = '9999999999999'
    if (len(from_timestamp) != 13) or (len(to_timestamp) != 13):
        error_msg += "Please use miliseconds 13 digits timestamp! "
    if int(from_timestamp) > int(to_timestamp):
        error_msg += "From timestamp should be before to timestamp! "
    if "taker" in query_parameters:
        taker = request.args["taker"]
        if taker not in stats_lib.valid_tickers:
            error_msg += "taker ["+taker+"] is an invalid ticker! Available options are "+str(stats_lib.valid_tickers)+". "
    if "maker" in query_parameters:
        maker = request.args["maker"]
        if maker not in stats_lib.valid_tickers:
            error_msg += "maker ["+maker+"] is an invalid ticker! Available options are "+str(stats_lib.valid_tickers)+". "
    swap_data = stats_lib.fetch_local_swap_files()
    if "gui" in query_parameters:
        if request.args["gui"] not in stats_lib.valid_guis:
            error_msg += "GUI ["+request.args['gui']+"] is invalid! Available options are "+str(stats_lib.valid_guis)+". "
        else:
            swap_data = stats_lib.gui_filter(swap_data, request.args["gui"])
    if maker != 'All' or taker != 'All':
        swap_data = stats_lib.pair_filter(swap_data, maker, taker)
    success_rate = stats_lib.count_successful_swaps(swap_data, int(from_timestamp), int(to_timestamp))
    data = {
    "result": "success",
    "fail_events": success_rate[2],
    "fail_info": success_rate[3]
    }
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


@app.get('/atomicstats/api/v1.0/get_takers')
async def get_takers():
    print("get_takers")
    error_msg = ''
    maker = 'All'
    taker = 'All'
    query_parameters = request.args
    if "from" in query_parameters:
        from_timestamp = request.args["from"]
    else:
        from_timestamp = '0000000000000'
    if "to" in query_parameters:
        to_timestamp = request.args["to"]
    else:
        to_timestamp = '9999999999999'
    if (len(from_timestamp) != 13) or (len(to_timestamp) != 13):
        error_msg += "Please use miliseconds 13 digits timestamp! "
    if int(from_timestamp) > int(to_timestamp):
        error_msg += "From timestamp should be before to timestamp! "
    if "taker" in query_parameters:
        taker = request.args["taker"]
        if taker not in stats_lib.valid_tickers:
            error_msg += "taker ["+taker+"] is an invalid ticker! Available options are "+str(stats_lib.valid_tickers)+". "
    if "maker" in query_parameters:
        maker = request.args["maker"]
        if maker not in stats_lib.valid_tickers:
            error_msg += "maker ["+maker+"] is an invalid ticker! Available options are "+str(stats_lib.valid_tickers)+". "
    swap_data = stats_lib.fetch_local_swap_files()
    if "gui" in query_parameters:
        if request.args["gui"] not in stats_lib.valid_guis:
            error_msg += "GUI ["+request.args['gui']+"] is invalid! Available options are "+str(stats_lib.valid_guis)+". "
        else:
            swap_data = stats_lib.gui_filter(swap_data, request.args["gui"])
    if maker != 'All' or taker != 'All':
        swap_data = stats_lib.pair_filter(swap_data, maker, taker)
    success_rate = stats_lib.count_successful_swaps(swap_data, int(from_timestamp), int(to_timestamp))
    taker_addresses = success_rate[3]
    sorted_taker_address_keys = sorted(taker_addresses.keys(), key=lambda y: (taker_addresses[y]['total']))
    sorted_taker_address_keys.reverse()
    for address in sorted_taker_address_keys:
        num_failed = taker_addresses[address]['failed']
        num_success = taker_addresses[address]['successful']
        total = taker_addresses[address]['total']
        taker_addresses[address]['last_swap'] = datetime.utcfromtimestamp(taker_addresses[address]['last_swap']/1000).strftime('%d-%m-%Y %H:%M:%S')
        taker_addresses[address]['percentage'] = num_success/total*100
    if error_msg != '':
        data = {
        "result" : "error",
        "error" : error_msg
        }
    else:
        data = {
        "result": "success",
        "maker" : maker,
        "taker" : taker,
        "time_now" : int(timestamp_now)*1000,
        "taker_addresses": taker_addresses
        }
        if from_timestamp != '0000000000000':
            data.update({"from_timestamp": int(from_timestamp)})
        if to_timestamp != '9999999999999':
            data.update({"to_timestamp": int(to_timestamp)})
        if "gui" in query_parameters:
            data.update({"gui_filter": request.args['gui']})
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

# optional: pair, dates
# @app.route('/atomicstats/api/v1.0/get_volumes', methods=['GET'])

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    uvicorn.run(app, host="0.0.0.0", port=8000, access_log=False, log_level='info')