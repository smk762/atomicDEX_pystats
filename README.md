API for seed node jsons parser

WIP!

Calls:

1) get swaps success rate

`/atomicstats/api/v1.0/get_success_rate`

returns success rate for all files on seed node

optional args:

`pair` - in format TICKER_TICKER (e.g. KMD_BTC) filter data for ticker
`from` - 13 digits timestamp (miliseconds epoch)
`to` - 13 digits timestamp (miliseconds epoch)

 these args possible to combine, e.g. `/atomicstats/api/v1.0/get_success_rate?pair=BTC_KMD&from=1564658276000&to=156690467900`


2) get swaps volume (wip)

`/atomicstats/api/v1.0/get_volumes`
