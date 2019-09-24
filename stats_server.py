#!/usr/bin/env python3
import flask
from flask import json, request
import stats_lib

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "<h1>AtomicDEX Stats</h1><p>Prototype API for AtomicDEX stats</p>"

# optional: pair, dates
@app.route('/atomicstats/api/v1.0/get_success_rate', methods=['GET'])
def get_volumes():
    query_parameters = request.args
    if "pair" in query_parameters and "from" in query_parameters and "to" in query_parameters:
        pair = request.args["pair"]
        tickers = request.args["pair"].split("_")
        try:
            pair_filtered_data = stats_lib.pair_filter(stats_lib.fetch_local_swap_files(), tickers[0], tickers[1])
        except IndexError:
            data = {
            "result" : "error",
            "error" : "not valid tickers"
            }
            response = app.response_class(
                response=json.dumps(data),
                status=400,
                mimetype='application/json'
            )
            return response
        if (len(request.args["from"]) != 13) or (len(request.args["to"]) != 13):
            data = {
            "result" : "error",
            "error" : "please use miliseconds 13 digits timestamp"
            }
            response = app.response_class(
                response=json.dumps(data),
                status=400,
                mimetype='application/json'
            )
            return response
        if int(request.args["from"]) > int(request.args["to"]):
            data = {
            "result" : "error",
            "error" : "from date should be before to date"
            }
            response = app.response_class(
                response=json.dumps(data),
                status=400,
                mimetype='application/json'
            )
            return response

        time_filtered_data = stats_lib.time_filter(pair_filtered_data, int(request.args["from"]), int(request.args["to"]))
        success_rate = stats_lib.count_successful_swaps(time_filtered_data)
    elif "pair" in query_parameters and "date" not in query_parameters:
        pair = request.args["pair"]
        tickers = request.args["pair"].split("_")
        pair_filtered_data = stats_lib.pair_filter(stats_lib.fetch_local_swap_files(), tickers[0], tickers[1])
        success_rate = stats_lib.count_successful_swaps(pair_filtered_data)
    elif "pair" not in query_parameters and "date" in query_parameters:
        pair = "all"
        time_filtered_data = stats_lib.time_filter(pair_filtered_data, int(request.args["from"]), int(request.args["to"]))
        success_rate = stats_lib.count_successful_swaps(time_filtered_data)
    else:
        success_rate = stats_lib.count_successful_swaps(stats_lib.fetch_local_swap_files())
        pair = "all"
    data = {
    "result": "success",
    "pair" : pair,
    "total": success_rate[1] + success_rate[0],
    "successful": success_rate[1],
    "failed": success_rate[0],
    "fail_events": success_rate[2]
    }
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/atomicstats/api/v1.0/get_fail_data', methods=['GET'])
def get_fails():
    query_parameters = request.args
    if "pair" in query_parameters and "from" in query_parameters and "to" in query_parameters:
        pair = request.args["pair"]
        tickers = request.args["pair"].split("_")
        try:
            pair_filtered_data = stats_lib.pair_filter(stats_lib.fetch_local_swap_files(), tickers[0], tickers[1])
        except IndexError:
            data = {
            "result" : "error",
            "error" : "not valid tickers"
            }
            response = app.response_class(
                response=json.dumps(data),
                status=400,
                mimetype='application/json'
            )
            return response
        if (len(request.args["from"]) != 13) or (len(request.args["to"]) != 13):
            data = {
            "result" : "error",
            "error" : "please use miliseconds 13 digits timestamp"
            }
            response = app.response_class(
                response=json.dumps(data),
                status=400,
                mimetype='application/json'
            )
            return response
        if int(request.args["from"]) > int(request.args["to"]):
            data = {
            "result" : "error",
            "error" : "from date should be before to date"
            }
            response = app.response_class(
                response=json.dumps(data),
                status=400,
                mimetype='application/json'
            )
            return response

        time_filtered_data = stats_lib.time_filter(pair_filtered_data, int(request.args["from"]), int(request.args["to"]))
        success_rate = stats_lib.count_successful_swaps(time_filtered_data)
    elif "pair" in query_parameters and "date" not in query_parameters:
        pair = request.args["pair"]
        tickers = request.args["pair"].split("_")
        pair_filtered_data = stats_lib.pair_filter(stats_lib.fetch_local_swap_files(), tickers[0], tickers[1])
        success_rate = stats_lib.count_successful_swaps(pair_filtered_data)
    elif "pair" not in query_parameters and "date" in query_parameters:
        pair = "all"
        time_filtered_data = stats_lib.time_filter(pair_filtered_data, int(request.args["from"]), int(request.args["to"]))
        success_rate = stats_lib.count_successful_swaps(time_filtered_data)
    else:
        success_rate = stats_lib.count_successful_swaps(stats_lib.fetch_local_swap_files())
        pair = "all"
    data = {
    "result": "success",
    "fail_events": success_rate[2],
    "fail_info": success_rate[3],
    }
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

# optional: pair, dates
# @app.route('/atomicstats/api/v1.0/get_volumes', methods=['GET'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=3134)
