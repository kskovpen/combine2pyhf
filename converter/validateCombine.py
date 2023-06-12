#!/usr/bin/python3

import os, sys, glob
from HiggsAnalysis.CombinedLimit.DatacardParser import *

def compare(lh, rh):
    if isinstance(lh, list):
        lh.sort()
        rh.sort()
        return True if lh == rh else False
    elif isinstance(lh, dict):
        shared = {k: lh[k] for k in lh if k in rh and lh[k] == rh[k]}
        return True if len(shared) == len(lh.items()) else False
    elif isinstance(lh, set):
        diff = lh.difference(rh)
        return not bool(diff)
    return False

opts = type("opts", (object,), dict(bin=True, noJMax=False, stat=False, nuisancesToExclude=[], allowNoSignal=True, allowNoBackground=True))

ws = os.environ['WS']

wdir = ws+'/validation/cards/combine/pyhf2combine'

runs = glob.glob(wdir+'/*/')
for r in runs:
    fcv = glob.glob(wdir+'/'+r.split('/')[-1]+'/*.txt')
    print('Validate ', r)

    for f in fcv:
        print('-> ', f)
        with open(f, 'r') as fdv:
            dcv = parseCard(fdv, opts)
        with open(f.replace('validation/', '').replace('pyhf2combine/', ''), 'r') as fdo:
            dco = parseCard(fdo, opts)
        res = {}
        res['bins'] = compare(dco.bins, dcv.bins)
        res['obs'] = compare(dco.obs, dcv.obs)
        res['processes'] = compare(dco.processes, dcv.processes)
        res['signals'] = compare(dco.signals, dcv.signals)
        res['isSignal'] = compare(dco.isSignal, dcv.isSignal)
        res['keyline'] = compare(dco.keyline, dcv.keyline)
        res['exp'] = compare(dco.exp, dcv.exp)
        res['systs'] = compare(dco.systs, dcv.systs)
        res['shapeMap'] = compare(dco.shapeMap, dcv.shapeMap)
        res['flatParamNuisances'] = compare(dco.flatParamNuisances, dcv.flatParamNuisances)
        res['rateParams'] = compare(dco.rateParams, dcv.rateParams)
        res['extArgs'] = compare(dco.extArgs, dcv.extArgs)
        res['rateParamsOrder'] = compare(dco.rateParamsOrder, dcv.rateParamsOrder)
        res['frozenNuisances'] = compare(dco.frozenNuisances, dcv.frozenNuisances)
        for k in res.keys():
            if not res[k]:
                print('Validation failed for '+k)

