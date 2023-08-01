#!/usr/bin/python3

import os, sys, glob, ROOT, logging, subprocess
from HiggsAnalysis.CombinedLimit.DatacardParser import *

ws = os.environ['WS']
wd = ws+'/validation'
wdir = wd+'/cards/combine/pyhf2combine'

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=ws+'/logs/validateCombine.log',
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
    try:
        for hname in lh.keys():
            if lh[hname].Integral() != rh[hname].Integral():
                hists.append(hname)
            else:
                for b in range(1, lh[hname].GetXaxis().GetNbins()+1):
                    if (lh[hname].GetBinContent(b) != rh[hname].GetBinContent(b)) or (lh[hname].GetBinError(b) != rh[hname].GetBinError(b)):
                        hists.append(hname)
                        break
    except Exception as e:
        comblog.error(e)
    return hists

opts = type("opts", (object,), dict(bin=True, noJMax=False, stat=False, nuisancesToExclude=[], allowNoSignal=True, allowNoBackground=True))

runs = glob.glob(wdir+'/*/')
for r in runs:
    runName = r.split('/')[-2]
    fcv = glob.glob(wdir+'/'+runName+'/*.txt')
    comblog.info('Validate '+runName+' (combine)')

    for f in fcv:
        forig = f.replace('validation/', '').replace('pyhf2combine/', '')
        with open(f, 'r') as fdv:
            dcv = parseCard(fdv, opts)
        with open(forig, 'r') as fdo:
            dco = parseCard(fdo, opts)
        comblog.info('--> Compare datacards: '+os.path.splitext(forig.split('/')[-1])[0])
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
                print('Original:', res[k][1])
                print('Converted:', res[k][2])
                passedCard = False
                
        if passedCard:
            comblog.info('--> Compare datacards: \033[1;32mpassed\x1b[0m')
            comblog.info('--> Compare shapes: '+os.path.splitext(forig.split('/')[-1])[0])
            histso, histsv = {}, {}
            for b in dco.shapeMap.keys():
                for p in dco.shapeMap[b].keys():
                    rfileo = dco.shapeMap[b][p][0]
                    rfilev = dcv.shapeMap[b][p][0]
                    rfo = ROOT.TFile(rfileo, 'READ')
                    rfv = ROOT.TFile(rfilev, 'READ')
                    nomo = dco.shapeMap[b][p][1]
                    nomv = dcv.shapeMap[b][p][1]
                    syso = dco.shapeMap[b][p][2]
                    sysv = dcv.shapeMap[b][p][2]
                    systNames = [s[0] for s in dco.systs]
                    for proc in dco.processes:
                        for syst in ['']+systNames:
                            if syst == '':
                                nomName = nomo.replace('$PROCESS', proc)
                                if not rfo.GetListOfKeys().Contains(nomName): continue
                                histso[b+'_'+proc] = rfo.Get(nomName).Clone(b+'_'+proc+'_original')
                                histso[b+'_'+proc].SetDirectory(0)
                                nomName = nomv.replace('$PROCESS', proc)
                                if not rfv.Get(nomName):
                                    comblog.error('Missing histogram in the converted file: '+nomName)
                                    continue
                                histsv[b+'_'+proc] = rfv.Get(nomName).Clone(b+'_'+proc+'_converted')
                                histsv[b+'_'+proc].SetDirectory(0)
                            else:
                                for var in ['Up', 'Down']:
                                    systName = syso.replace('$PROCESS', proc).replace('$SYSTEMATIC', syst+var)
                                    if not rfo.GetListOfKeys().Contains(systName): continue
                                    histso[b+'_'+proc+'_'+syst+var] = rfo.Get(systName).Clone(systName+'_original')
                                    histso[b+'_'+proc+'_'+syst+var].SetDirectory(0)
                                    systName = sysv.replace('$PROCESS', proc).replace('$SYSTEMATIC', syst+var)
                                    if not rfv.Get(systName):
                                        comblog.error('Missing histogram in the converted file: '+systName)
                                        continue
                                    histsv[b+'_'+proc+'_'+syst+var] = rfv.Get(systName).Clone(systName+'_converted')
                                    histsv[b+'_'+proc+'_'+syst+var].SetDirectory(0)

            hists = compareShapes(histso, histsv)
            
            if not hists:
                comblog.info('--> Compare shapes: \033[1;32mpassed\x1b[0m')
            else:
                comblog.info('--> Compare shapes: \033[1;31mfailed\x1b[0m')
                for h in hists:
                    nbins = histso[h].GetXaxis().GetNbins()
                    comblog.error('--> Original shape ('+h+'):')
                    for b in range(1, nbins+1):
                        comblog.error('bin #'+str(b)+': '+str(histso[h].GetBinContent(b))+'+-'+str(histso[h].GetBinError(b)))
                    comblog.error('--> Converted shape ('+h+'):')
                    for b in range(1, nbins+1):
                        comblog.error('bin #'+str(b)+': '+str(histsv[h].GetBinContent(b))+'+-'+str(histsv[h].GetBinError(b)))