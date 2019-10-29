API for seed node jsons parser

WIP!

Calls:

1) get swaps success rate

`/atomicstats/api/v1.0/get_success_rate`

Returns success rate for all files on seed node

Optional args:

`maker` - TICKER of coin traded from maker  
`taker` - TICKER of coin traded to taker  
`from` - 13 digits timestamp (miliseconds epoch)  
`to` - 13 digits timestamp (miliseconds epoch)  
`gui` - filters results based on GUI used by maker (if set in maker's MM2.json). 

Examples:
these args possible to combine, e.g. `/atomicstats/api/v1.0/get_success_rate?pair=BTC_KMD&from=1564658276000&to=156690467900`


2) get swaps volume (wip)

`/atomicstats/api/v1.0/get_volumes`
