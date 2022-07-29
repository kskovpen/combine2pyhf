#!/usr/bin/env python

import os, sys, math, ROOT
from scipy import stats
import numpy as np
from collections import OrderedDict

def plot(fname):
    procs = ['bkg3', 'bkg2', 'bkg1', 'sig']
    cols = [ROOT.kBlue-5, ROOT.kBlue-7, ROOT.kBlue-9, ROOT.kRed-7]
    c = ROOT.TCanvas()
    f = ROOT.TFile(fname, 'READ')
    hst = ROOT.THStack()
    hsum = None
    leg = ROOT.TLegend(0.20, 0.50, 0.40, 0.80)
    leg.SetBorderSize(0)
    leg.SetLineWidth(0)
    leg.SetLineColor(0)
    leg.SetFillStyle(0)
    leg.SetFillColor(0)
    for i, p in enumerate(procs):
        h = f.Get(p)
        h.SetLineColor(cols[i])
        h.SetFillColor(cols[i])
        hst.Add(h)
        if hsum == None: hsum = h.Clone('hsum')
        else: hsum.Add(h)
    hst.Draw('hist e1')
    h = f.Get('data_obs')
    h.Draw('e1 same')
    h.SetMarkerStyle(20)
    leg.AddEntry(h, 'Data', 'lp')
    for i, p in enumerate(reversed(procs)):
        leg.AddEntry(hst.GetHists()[len(procs)-i-1], p, 'f')
    hst.GetHistogram().GetXaxis().SetTitle('Bins')
    hst.GetHistogram().GetYaxis().SetTitle('Events')
    hst.SetMaximum(max(hsum.GetMaximum(), h)*1.2)
    leg.Draw()
    c.Print('shapes-test.pdf')

ROOT.gROOT.SetBatch()
    
h = {}
nBins = 10
nev = OrderedDict({'sig': 50000, 'bkg1': 5000, 'bkg2': 5000, 'bkg3': 5000})
syst = OrderedDict({'sig': [{'normsys': 1.20}, \
{'shape': list(np.random.uniform(0.8, 1.2, nBins))}], \
'bkg1': [{'bkg1norm_normsys': 1.30}, \
{'shape1': list(np.random.uniform(0.7, 1.3, nBins))}], \
'bkg2': [{'bkg2norm_normsys': 1.15}, \
{'rate_rateparam': 0.7}],
'bkg3': [{'bkg3norm_normsys': 1.20}, \
{'shape3': list(np.random.uniform(0.85, 1.15, nBins))}]})

f = ROOT.TFile('shapes-test.root', 'RECREATE')

htot = ROOT.TH1F('tot', 'tot', nBins, 0., nBins)

for p in nev.keys():
    h[p] = ROOT.TH1F(p, p, nBins, 0., nBins)
    if p in ['sig']:
        data = np.random.exponential(1, nev[p])
    elif p in ['bkg1']:
        data = np.random.exponential(2, nev[p])
    elif p in ['bkg2']:
        data = np.random.exponential(10, nev[p])
    elif p in ['bkg3']:
        data = np.random.uniform(0., nBins, nev[p])
    else: continue
    for d in data: 
        if p not in ['sig', 'bkg1']: h[p].Fill(d)
        else: h[p].Fill(nBins-d)
    if p in ['bkg2']:
       h[p].Scale(0.05)
    elif p in ['bkg1']:
       h[p].Scale(0.02)
    elif p in ['bkg3']:
       h[p].Scale(0.01)
    elif p in ['sig']:
       h[p].Scale(0.001)
    h[p].Write()
    print(p+' =', h[p].Integral())
    
    hsyst = h[p].Clone('hsyst')
       
    if p in syst.keys():
        for syss in syst[p]:
            for k, v in syss.items():
                if 'norm' in k:
                    for ib in range(nBins):
                        nom = hsyst.GetBinContent(ib+1)
                        shifted = nom + np.random.normal(0.,hsyst.GetBinContent(ib+1)*(v-1.0), 1)[0]
                        shifted = shifted if shifted > 0 else 0.
                        hsyst.SetBinContent(ib+1, shifted)
                elif 'rate' in k:
                    for ib in range(nBins):
                        nom = hsyst.GetBinContent(ib+1)
                        shifted = nom*v
                        hsyst.SetBinContent(ib+1, shifted)
                elif 'shape' in k:
                    for j in [-1, 1]:
                        hsystsep = h[p].Clone('hsystsep')
                        for ib in range(nBins):
                            nomm = h[p].GetBinContent(ib+1)
                            shifted = abs(nomm*v[ib]-nomm)*j+nomm
                            shifted = shifted if shifted > 0 else 0.
                            hsystsep.SetBinContent(ib+1, shifted)
                        hsystsep.SetName(p+'_'+k+('Up' if j == 1 else 'Down'))
                        hsystsep.Write()
                        for ib in range(nBins):
                            nom = hsyst.GetBinContent(ib+1)
                            shifted = abs(nom*v[ib]-nom)*j+nom
                            shifted = shifted if shifted > 0 else 0.
                            hsyst.SetBinContent(ib+1, shifted)
                else:
                    print('Uknown systematics type found')
                    sys.exit()

    htot.Add(hsyst)
    
data_obs = htot.Clone('data_obs')
for ib in range(nBins):
    v = data_obs.GetBinContent(ib+1)
    if v > 3.0:
        vg = int(np.random.normal(loc=v, scale=math.sqrt(v), size=1)[0])
        err = math.sqrt(vg)
    else: 
        vg = np.random.poisson(lam=v, size=1)[0]
        err = vg-stats.poisson.interval(0.68, vg)[0]
    data_obs.SetBinContent(ib+1, vg)
    data_obs.SetBinError(ib+1, err)
print('Data =', data_obs.Integral())
data_obs.Write()
    
f.Close()

plot('shapes-test.root')
