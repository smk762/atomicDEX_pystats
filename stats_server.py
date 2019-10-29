#!/usr/bin/env python3
import flask
from flask import json, request
import stats_lib
from datetime import datetime, timezone

app = flask.Flask(__name__)
app.config["DEBUG"] = True


valid_tickers = ["AXE","BAT","BCH","BOTS","BTC","BTCH","CHIPS","COMMOD",
                "COQUI","CRYPTO","DAI","DASH","DEX","DGB","DOGE","ETH",
                "HUSH","KMD","KMDICE","LABS","LINK","LTC","MORTY","OOT",
                "PAX","QTUM","REVS","RVN","RFOX","RICK","SUPERNET","THC",
                "USDC","TUSD","VRSC","WLC","ZEC","ZEXO","ZILLA"]

now = datetime.now()
timestamp_now = datetime.timestamp(now)

@app.route('/', methods=['GET'])
def home():
    return "<h1>AtomicDEX Stats</h1><p>Prototype API for AtomicDEX stats</p>"

# optional: pair, dates
@app.route('/atomicstats/api/v1.0/get_success_rate', methods=['GET'])
def get_volumes():
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
        if taker not in valid_tickers:
            error_msg += "taker ["+taker+"] is an invalid ticker! Available options are "+str(valid_tickers)+". "
    if "maker" in query_parameters:
        maker = request.args["maker"]
        if maker not in valid_tickers:
            error_msg += "maker ["+maker+"] is an invalid ticker! Available options are "+str(valid_tickers)+". "
    swap_data = stats_lib.fetch_local_swap_files()
    print(len(swap_data))
    if "gui" in query_parameters:
        gui_swap_data = stats_lib.gui_filter(swap_data, request.args["gui"])
        swap_data = gui_swap_data[0]
        print(len(swap_data))
        valid_guis = gui_swap_data[1]
        if request.args["gui"] not in valid_guis:
            error_msg += "GUI ["+request.args['gui']+"] is invalid! Available options are "+str(valid_guis)+". "
    if maker != 'All' or taker != 'All':
        swap_data = stats_lib.pair_filter(swap_data, maker, taker)
    print(len(swap_data))          
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
        status=400,
        mimetype='application/json'
    )
    return response

# optional: pair, dates
# @app.route('/atomicstats/api/v1.0/get_volumes', methods=['GET'])

if __name__ == '__main__':
#    app.run(host= '127.0.0.1', debug=True)
    app.run(host= '0.0.0.0', debug=True)
