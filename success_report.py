#!/usr/bin/env python3
import stats_lib
import requests
from datetime import datetime, timezone

now = datetime.now()
timestamp_now = datetime.timestamp(now)


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

hl = colorize(" | ", 'lightblue')

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
ignored_addresses = ['RDbAXLCmQ2EN7daEZZp7CC9xzkcN8DfAZd']
smk_addresses = ['R9ViegsR8qrthx81NJdANfnkLoQxomzHAM', 'RDvm5qF3FaBuHe4oT1gwyC25iCFNcNeqz4', 'RVoEJTxKqBkW9KLFiQHrahxYmcJNtEu2Ui', 
                 'RXe7VTtAHeQeGMk8Y9xKXZAZpDHHo7BQNT', 'RUwodWWAabv3h2jSatVDSMT89cLkTMSutA', 'RDvWMrz4B597R9WvzC6Kzsxwuz2wsR1ptZ', 
                 'R9LzCsxtWZvp6fhuTEtS9sRLpCFmv7cqjC']
known_addr = [{"Oszy":["RW5LqPVTNk2V94xL9j5485TEpQEqjNotyq"]}]

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

while True:
    specify_time = input("Specify time range? [y/n]: ")
    if specify_time == 'y' or specify_time == 'Y':
        specify_time = True
        break
    elif specify_time == 'n' or specify_time == 'N':
        specify_time = False
        break
    else:
        print("Please enter [Y/y] or [N/n] only!")
if specify_time:
    start_timestamp = get_ts("Enter Start date")
    start_time_str = datetime.utcfromtimestamp(start_timestamp/1000).strftime('%d-%m-%Y')
    end_timestamp = get_ts("Enter End date")
    while end_timestamp < start_timestamp:
        print(colorize("Time does not flow backwards... yet. Please input an end date which is after "+start_time_str+"!", 'red'))
        end_timestamp = get_ts("Enter End date")
else:
    start_timestamp = 0
    end_timestamp = int(timestamp_now)*1000

start_time_str = datetime.utcfromtimestamp(start_timestamp/1000).strftime('%d-%m-%Y %H:%M:%S')
end_time_str = datetime.utcfromtimestamp(end_timestamp/1000).strftime('%d-%m-%Y %H:%M:%S')

data = stats_lib.fetch_local_swap_files()
success_rates = stats_lib.count_successful_swaps(data, start_timestamp, end_timestamp)

for failed_swap in success_rates[2]:
    for error_event in maker_error_events_count:
        if success_rates[2][failed_swap]["maker_fail_event_type"] == error_event:
            maker_error_events_count[error_event] += 1

taker_addresses = success_rates[3]
gui_data = success_rates[4]
failing_address = 0
winning_address = 0
max_fail = 0
max_win = 0
i = 0
j = 0
pct_gt95 = 0
pct_75_to_95 = 0
pct_50_to_75 = 0
pct_25_to_50 = 0
pct_lt_25 = 0
while True:
    show_addr = input("Show addresses table? [y/n]: ")
    if show_addr == 'y' or show_addr == 'Y':
        show_addr = True
        break
    elif show_addr == 'n' or show_addr == 'N':
        show_addr = False
        break
    else:
        print("Please enter [Y/y] or [N/n] only!")
if show_addr:
    header = hl+'{:^76}'.format('ADDRESS / PUBKEY')+hl+'{:^10}'.format('FAILED')+hl+'{:^10}'.format('SUCCESS') \
            +hl+'{:^10}'.format('TOTAL')+hl+'{:^10}'.format('PERCENT')+hl+'{:^20}'.format('LAST SWAP')+hl
    row_line = "-"*155
    print(" "+row_line)
    print(header)
    print(" "+row_line)
sorted_taker_address_keys = sorted(taker_addresses.keys(), key=lambda y: (taker_addresses[y]['total']))
sorted_taker_address_keys.reverse()
for address in sorted_taker_address_keys:
    if address not in ignored_addresses:
        if address in smk_addresses:
            address_str = address+" (smk762)"
        else:
            address_str = address
        i += 1
        num_failed = taker_addresses[address]['failed']
        num_success = taker_addresses[address]['successful']
        total = taker_addresses[address]['total']
        last_swap = datetime.utcfromtimestamp(taker_addresses[address]['last_swap']/1000).strftime('%d-%m-%Y %H:%M:%S')
        perc = num_success/total*100
        if perc > 95:
            perc = colorize('{:^10}'.format(str(perc)[:6]+"%"), 'green')
            address_str = colorize('{:^76}'.format(str(address_str)), 'green')
            pct_gt95 += 1
        elif perc > 75:
            perc = colorize('{:^10}'.format(str(perc)[:6]+"%"), 'cyan')
            address_str = colorize('{:^76}'.format(str(address_str)), 'cyan')
            pct_75_to_95 += 1
        elif perc > 50:
            perc = colorize('{:^10}'.format(str(perc)[:6]+"%"), 'orange')
            address_str = colorize('{:^76}'.format(str(address_str)), 'orange')
            pct_50_to_75 += 1
        elif perc > 25:
            perc = colorize('{:^10}'.format(str(perc)[:6]+"%"), 'pink')
            address_str = colorize('{:^76}'.format(str(address_str)), 'pink')
            pct_25_to_50 += 1
        else:
            perc = colorize('{:^10}'.format(str(perc)[:6]+"%"), 'red')
            address_str = colorize('{:^76}'.format(str(address_str)), 'red')
            pct_lt_25 += 1
        row = hl+'{:^76}'.format(address_str)+hl+'{:^10}'.format(str(num_failed))+hl+'{:^10}'.format(str(num_success))+hl+'{:^10}'.format(str(total)) \
             +hl+'{:^10}'.format(str(perc))+hl+'{:^20}'.format(str(last_swap))+hl
        if show_addr:
            print(row)
        if i == 50:
            j += 1
            if show_addr:
                print(" "+row_line)
                input('{:^155}'.format("["+str((j-1)*i)+" to "+str(j*i)+" of "+str(len(sorted_taker_address_keys))+"] Press [Enter] to continue..."))
                print()
                print(" "+row_line)
                print(header)
                print(" "+row_line)
            i = 0
        if num_failed > 0:
            failing_address += 1
        if num_success > 0:
            winning_address += 1
    else:
        if show_addr:
            print(address+ "is ignored.")
if show_addr:
    print(" "+row_line)
    print(header)
    print(" "+row_line)

if success_rates[0]+success_rates[1] != 0:
    print("\nSwap data for time range ["+start_time_str+" to "+end_time_str+"]\n")
    print("=== Swap Stats ===")
    print("Total swaps: " + str(success_rates[0] + success_rates[1]))
    print("Total failed swaps: " + str(success_rates[0]))
    print("Total successful swaps: " + str(success_rates[1]))
    print("Success ratio: " + str(success_rates[1] / (success_rates[0] + success_rates[1]) * 100)[:6]+"%")
    print("\n=== Address Stats ===")
    print("Total taker addresses: " + str(len(success_rates[3])))
    print("Addresses with failed swaps: " + str(failing_address))
    print("Addresses with successful swaps: " + str(winning_address))
    print("Addresses with > 95% success rate: " + str(pct_gt95))
    print("Addresses with 75 - 95% success rate: " + str(pct_75_to_95))
    print("Addresses with 50 - 75% success rate: " + str(pct_50_to_75))
    print("Addresses with 25 - 50% success rate: " + str(pct_25_to_50))
    print("Addresses with < 25% success rate: " + str(pct_lt_25))
    print("\n=== Fail Event Stats ===")
    for error_event in maker_error_events_count:
        print("Failed for maker on stage '" + error_event + "' : " + str(maker_error_events_count[error_event]))
    print("\n=== GUI Stats ===")
    for gui in gui_data:
        print("GUI ["+gui+"] successful: " + str(gui_data[gui]['successful']))
        print("GUI ["+gui+"] failed: " + str(gui_data[gui]['failed']))
        rate = round(gui_data[gui]['successful']/(gui_data[gui]['successful']+gui_data[gui]['failed']),1)
        print("GUI ["+gui+"] rate: " + str(rate*100)+"%\n")
else:
    print(colorize("\nNo swap data for specified time range ["+start_time_str+" to "+end_time_str+"]!", 'red'))
