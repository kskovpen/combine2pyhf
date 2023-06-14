#!/usr/bin/python3

import os, sys, glob, ROOT, logging, subprocess
from HiggsAnalysis.CombinedLimit.DatacardParser import *

ws = os.environ['WS']
wd = ws+'/validation'
wdir = wd+'/cards/combine/pyhf2combine'

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=wd+'/cards/combine/validateCombine.log',
                    filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

logging.info('Start validation process for combine card conversion')
comblog = logging.getLogger('convert.combine.validate')

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

runs = glob.glob(wdir+'/*/')
for r in runs:
    runName = r.split('/')[-2]
    fcv = glob.glob(wdir+'/'+runName+'/*.txt')
    comblog.info('Validate '+r)

    for f in fcv:
        forig = f.replace('validation/', '').replace('pyhf2combine/', '')
        with open(f, 'r') as fdv:
            dcv = parseCard(fdv, opts)
        with open(forig, 'r') as fdo:
            dco = parseCard(fdo, opts)
        comblog.info('--> Compare datacards')
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
                comblog.error('Datacard comparison failed for '+k+':')
                comblog.error(res[k][1]+' '+res[k][2])
                passedCard = False
                
        if passedCard:
            comblog.info('--> Compare shapes')
            for b in dco.shapeMap.keys():
                for p in dco.shapeMap[b].keys():
                    rfileo = dco.shapeMap[b][p][0]
                    rfilev = dcv.shapeMap[b][p][0]
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
                    if hists:
                        comblog.error('Shape comparison failed, more info below:')
                    for h in hists:
                        nbins = histso[h].GetXaxis().GetNbins()
                        comblog.error('--> Original shape ('+h+'):')
                        for b in range(1, nbins+1):
                            comblog.error('bin #'+b+': '+histso[h].GetBinContent(b)+'+-'+histso[h].GetBinError(b))
                        comblog.error('--> Converted shape ('+h+'):')
                        for b in range(1, nbins+1):
                            comblog.error('bin #'+b+': '+histsv[h].GetBinContent(b)+'+-'+histsv[h].GetBinError(b))