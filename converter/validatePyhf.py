#!/usr/bin/python3

import os, sys, pyhf, json, glob

ws = os.environ['WS']

fcv = glob.glob(ws+'/validation/cards/pyhf/combine2pyhf/*.json')

for f in fcv:
    with open(f, 'r') as fdv:
        dcv = parseCard(fdv, opts)
    with open(f.replace('validation/', '').replace('combine2pyhf/', ''), 'r') as fdo:
        dco = parseCard(fdo, opts)
    res = {}
    print(f)
    for k in res.keys():
        if not res[k]:
            print('Validation failed for '+k)
                                