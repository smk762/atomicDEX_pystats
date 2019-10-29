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
`/atomicstats/api/v1.0/get_success_rate?from=1564658276000`
`/atomicstats/api/v1.0/get_success_rate?to=156690467900`
`/atomicstats/api/v1.0/get_success_rate?maker=LABS`
`/atomicstats/api/v1.0/get_success_rate?taker=KMD`
`/atomicstats/api/v1.0/get_success_rate?gui=atomicDEX 0.2.5 Android`

These args can be combined: 
`/atomicstats/api/v1.0/get_success_rate?gui=atomicDEX 0.2.5 Android&maker=LABS&taker=KMD&from=1564658276000&to=156690467900`


2) get swaps volume (wip)

`/atomicstats/api/v1.0/get_volumes`
