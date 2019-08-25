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
    if "pair" in query_parameters and "date" in query_parameters:
        #TODO: implement - note that need to convert human readable data into 13 digits timestamp
        success_rate = "success rate with pair and date filters"
    elif "pair" in query_parameters and "date" not in query_parameters:
        #TODO: handle crash on not correct ticker usage
        pair = request.args["pair"]
        tickers = request.args["pair"].split("_")
        success_rate = stats_lib.count_successful_swaps(stats_lib.pair_filter(stats_lib.fetch_local_swap_files(), tickers[0], tickers[1]))
    elif "pair" not in query_parameters and "date" in query_parameters:
        #TODO: implement
        success_rate = "success rate for dates"
        pair = "stub"
    else:
        success_rate = stats_lib.count_successful_swaps(stats_lib.fetch_local_swap_files())
        pair = "all"
    data = {
    "pair" : pair,
    "total": success_rate[1] + success_rate[0],
    "successful": success_rate[1],
    "failed": success_rate[0]
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
    app.run(debug=True)
