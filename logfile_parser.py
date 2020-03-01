#!/usr/bin/env python3
import json

log_swaps = {}
addresses = []
address_swaps = {}
swaplist = {}
with open("merged_logs.txt", "r") as f:
    lines = f.readlines()
    x = 0
    for line in lines:
        x += 1
        # Remove log data not during stress test
        if line.find('NoSuchMethodError') == -1 and line.find('JsonRpcError') == -1  and line.find('Transport error') == -1:
            if line.find('2019-10-31') > -1 or line.find('2019-11-01') > -1:
                # Get R-address of User
                if line.find('getBalance') > -1:
                        try:
                            balance_json = " ".join(line.split(" ")[3:])[1:]
                            balance_info = json.loads(balance_json)
                            if balance_info['coin'] == 'RICK' or balance_info['coin'] == 'MORTY':
                                address = balance_info['address']
                                if address not in addresses:
                                    addresses.append(address)
                        except Exception as e:
                            pass
                    # Get recent swaps json
                if line.find('getRecentSwaps') > -1:
                    try:
                        swap_json = " ".join(line.split(" ")[3:])[1:]
                        swap_results = json.loads(swap_json)['result']['swaps']
                        for swap in swap_results: 
                            if swap['type'] == 'Taker':
                                folder = "TAKER"
                            elif swap['type'] == 'Maker':
                                folder = "MAKER"
                            uuid = swap['uuid']
                            with open(folder+"/"+uuid+".json", "w") as j:
                                print("writing "+folder+"/"+uuid+".json")
                                j.write(json.dumps(swap))
                    except json.decoder.JSONDecodeError:
                        pass

print(addresses)
