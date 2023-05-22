#!/usr/bin/python3

import os, sys, math, json
import numpy as np
from optparse import OptionParser
import ROOT

def main(argv = None):
    
    if argv == None:
        argv = sys.argv[1:]
        
    usage = "usage: %prog [options]\n Convert pyhf json to combine datacard"
    
    parser = OptionParser(usage)
    parser.add_option("--input", default='datacard.json', help="Input pyhf json file [default: %default]")
    parser.add_option("--output", default='datacard', help="Output combine datacard file name [default: %default]")
    
    (options, args) = parser.parse_args(sys.argv[1:])
    
    return options

if __name__ == '__main__':
    
    options = main()
    
    d = json.load(open(options.input))
    
    f = ROOT.TFile(options.output+'.root', "RECREATE")
    
    h = {}
    
    # BB-lite check
    bbl = False
    for ch in d['channels']:
        for s in ch['samples']:
            stat = []
            for m in s['modifiers']:
                if 'prop' in m['name'] and m['type'] == 'staterror':
                    if m['name'] in stat:
                        bbl = True
                        break
                    else: stat.append(m['name'])
            if bbl: break
        if bbl: break
                    
    # Create shape file
    samples = []
    poi = ''
    for ch in d['channels']:
        f.mkdir(ch['name']);
        for s in ch['samples']:
            if s not in samples: samples.append(s)
            hname = ch['name']+'/'+s['name']
            data = s['data']
            nb = len(data)
            h[hname] = ROOT.TH1F(hname, hname, nb, array('f', list(np.arange(nb+1))))
            for i in range(len(data)):
                h[hname].SetBinContent(i+1, data[i])
                for m in s['modifiers']:
                    if m['type'] == 'normfactor' and 'r_' in m['name']:
                        poi = s
                    if 'prop' in m['name']:
                        h[hname].SetBinError(i+1, m['data'][i])
                        
        for obs in d['observations']:
            if obs['name'] == ch['name']:
                hname = ch['name']+'/data_obs'
                data = s['data']
                nb = len(data)
                h[hname] = ROOT.TH1F(hname, hname, nb, array('f', list(np.arange(nb+1))))
                for i in range(len(data)):
                    h[hname].SetBinContent(i+1, data[i])
                    h[hname].SetBinError(i+1, math.sqrt(data[i]))
             
    f.Write()
    f.Close()
    
    # Create datacard
    nchan = len(d['channels'])
    samp = [poi]
    for s in samples:
        if s == poi: continue
        samp.append(s)
    nsamp = len(samp)
    dc = 'imax '+str(nchan)+' number of bins\\n'
    dc += 'jmax '+str(nsamp-1)+' number of processes minus 1\\n'
    dc += 'kmax 0 number of nuisance parameters\\n'
    dc += '------------------------------------\\n'
    for ch in d['channels']:
        dc += 'shapes * '+ch+' '+options.output.split('/')[-1]+'.root $PROCESS\\n'
    dc += '------------------------------------\\n'
    dc += 'bin          '+' '.join(d['channels'])+'\\n'
    dc += 'observation  '+np.repeat('-1 ', nchan)+'\\n'
    dc += '------------------------------------\\n'
    procbin, proc, procsamp, rate = [], [], [], []
    for ch in d['channels']:
        for i, s in enumerate(samp):
            procbin.append(ch)
            proc.append(s)
            procsamp.append(i)
            rate.append(-1)
    dc += 'bin          '+' '.join(procbin)+'\\n'
    dc += 'process      '+' '.join(proc)+'\\n'
    dc += 'process      '+' '.join(procsamp)+'\\n'
    dc += 'rate         '+' '.join(rate)+'\\n'
    dc += '------------------------------------\\n'
    if bbl: dc += 'ch1 autoMCStats 0 1 1\\n'
    else: dc += 'ch1 autoMCStats 0 100000 100000\\n'
    with open(options.output+'.txt', 'w') as f:
        f.close()
    