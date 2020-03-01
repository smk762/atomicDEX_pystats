#!/usr/bin/env python3
from lib import stats_lib

json_path = '/var/www/html/json'

swaps_summary = stats_lib.swaps_summary_json()
stats_lib.write_json(json_path, "All_swaps_summary.json", swaps_summary)
addresses_summary = stats_lib.address_summary_json(swaps_summary)
stats_lib.write_json(json_path, "All_address_summary.json", addresses_summary)

stress_test_start_timestamp = 1572523200000
stress_test_end_timestamp = 1572544800000
stress_test_time_swaps_summary = stats_lib.time_filter(swaps_summary, stress_test_start_timestamp, stress_test_end_timestamp)

stress_test_time_morty_swaps_summary = stats_lib.coin_filter(stress_test_time_swaps_summary, 'MORTY')
stress_test_time_morty_rick_swaps_summary = stats_lib.coin_filter(stress_test_time_morty_swaps_summary, 'RICK')
stats_lib.write_json(json_path, "stress_test_swaps_summary.json", stress_test_time_morty_rick_swaps_summary)

stress_test_time_morty_rick_addresses_summary = stats_lib.address_summary_json(stress_test_time_morty_rick_swaps_summary)
stats_lib.write_json(json_path, "stress_test_address_summary.json", stress_test_time_morty_rick_addresses_summary)
