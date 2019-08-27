API for seed node jsons parser

WIP!

Calls:

1) get swaps success rate

`/atomicstats/api/v1.0/get_success_rate`

returns success rate for all files on seed node

optional args:

`pair` - in format TICKER_TICKER (e.g. KMD_BTC) filter data for ticker
`date` - in format DDMMYY_DDMMYY - filter data for given dates range

 these args possible to combine, e.g. `/atomicstats/api/v1.0/get_success_rate?pair=BTC_KMD&date=010819_300819`


2) get swaps volume (wip)

`/atomicstats/api/v1.0/get_volumes`
