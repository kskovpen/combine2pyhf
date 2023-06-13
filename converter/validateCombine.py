#!/usr/bin/python3

import os, sys, glob, ROOT
from HiggsAnalysis.CombinedLimit.DatacardParser import *

def compareCards(lh, rh):
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

def compareShapes(lh, rh):
    hists = []
    for hname in lh.keys():
        if lh[hname].Integral() != rh[hname].Integral():
            hists.append(hname)
        else:
            for b in range(1, lh[hname].GetXaxis().GetNbins()+1):
                if (lh[hname].GetBinContent(b) != lr[hname].GetBinContent(b)) or (lh[hname].GetBinError(b) != lr[hname].GetBinError(b)):
                    hists.append(hname)
                    break
    return hists

opts = type("opts", (object,), dict(bin=True, noJMax=False, stat=False, nuisancesToExclude=[], allowNoSignal=True, allowNoBackground=True))

ws = os.environ['WS']

wdir = ws+'/validation/cards/combine/pyhf2combine'

runs = glob.glob(wdir+'/*/')
for r in runs:
    runName = r.split('/')[-2]
    fcv = glob.glob(wdir+'/'+runName+'/*.txt')
    print('Validate ', r)

    for f in fcv:
        forig = f.replace('validation/', '').replace('pyhf2combine/', '')
        with open(f, 'r') as fdv:
            dcv = parseCard(fdv, opts)
        with open(forig, 'r') as fdo:
            dco = parseCard(fdo, opts)
        print('--> Original datacard:', forig)
        print('--> Converted datacard:', f)
        res = {}
        res['bins'] = [compareCards(dco.bins, dcv.bins), dco.bins, dcv.bins]
        res['obs'] = [compareCards(dco.obs, dcv.obs), dco.obs, dcv.obs]
        res['processes'] = [compareCards(dco.processes, dcv.processes), dco.processes, dcv.processes]
        res['signals'] = [compareCards(dco.signals, dcv.signals), dco.signals, dcv.signals]
        res['isSignal'] = [compareCards(dco.isSignal, dcv.isSignal), dco.isSignal, dcv.isSignal]
        res['keyline'] = [compareCards(dco.keyline, dcv.keyline), dco.keyline, dcv.keyline]
        res['exp'] = [compareCards(dco.exp, dcv.exp), dco.exp, dcv.exp]
        res['systs'] = [compareCards(dco.systs, dcv.systs), dco.systs, dcv.systs]
#        res['shapeMap'] = [compareCards(dco.shapeMap, dcv.shapeMap), dco.shapeMap, dcv.shapeMap] # run an explicit comparison of shapes below
        res['flatParamNuisances'] = [compareCards(dco.flatParamNuisances, dcv.flatParamNuisances), dco.flatParamNuisances, dcv.flatParamNuisances]
        res['rateParams'] = [compareCards(dco.rateParams, dcv.rateParams), dco.rateParams, dcv.rateParams]
        res['extArgs'] = [compareCards(dco.extArgs, dcv.extArgs), dco.extArgs, dcv.extArgs]
        res['rateParamsOrder'] = [compareCards(dco.rateParamsOrder, dcv.rateParamsOrder), dco.rateParamsOrder, dcv.rateParamsOrder]
        res['frozenNuisances'] = [compareCards(dco.frozenNuisances, dcv.frozenNuisances), dco.frozenNuisances, dcv.frozenNuisances]
        
        passedCard = True
        for k in res.keys():
            if not res[k][0]:
                print('Validation failed for '+k+':')
                print(res[k][1], res[k][2])
                passedCard = False
                
        if passedCard:
            print('--> Compare shapes')
            for b in dco.shapeMap.keys():
                for p in dco.shapeMap[b].keys():
                    rfileo = dco.shapeMap[b][p][0]
                    rfilev = dcv.shapeMap[b][p][0]
                    print('Original shape file:', rfileo)
                    print('Converted shape file:', rfilev)
                    rfo = ROOT.TFile(wdir.replace('validation/', '').replace('pyhf2combine', '')+'/'+runName+'/'+rfileo, 'READ')
                    rfv = ROOT.TFile(rfilev, 'READ')
                    keyso = rfo.GetDirectory(b).GetListOfKeys()
                    keysv = rfv.GetDirectory(b).GetListOfKeys()
                    histso, histsv = {}, {}
                    for ho in keyso:
                        histso[ho.ReadObj().GetName()] = ho.ReadObj().Clone(ho.ReadObj().GetName()+'_original')
                    for hv in keysv:
                        histsv[hv.ReadObj().GetName()] = hv.ReadObj().Clone(hv.ReadObj().GetName()+'_converted')
                    hists = compareShapes(histso, histsv)
                    for h in hists:
                        print('Shape comparison failed for', h, '!')
                        nbins = histso[h].GetXaxis().GetNbins()
                        print('--> Original shape:')
                        for b in range(1, nbins+1):
                            print(b, histso[h].GetBinContent(b), histso[h].GetBinError(b))
                        print('--> Converted shape:')
                        for b in range(1, nbins+1):
                            print(b, histsv[h].GetBinContent(b), histsv[h].GetBinError(b))
                            