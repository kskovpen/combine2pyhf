#!/usr/bin/python3

import os, sys, math, json
import numpy as np
from array import array
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
    
    fr = ROOT.TFile(options.output+'.root', "RECREATE")
    
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
    samp = []
    poi = ''
    for ch in d['channels']:
        fr.cd()
        sd = fr.mkdir(ch['name']);
        sd.cd()
        for s in ch['samples']:
            if s not in samp: samp.append(s['name'])
            hname = s['name']
            hnamep = ch['name']+'_'+hname
            data = s['data']
            nb = len(data)
            h[hnamep] = ROOT.TH1F(hname, hname, nb, array('f', list(np.arange(nb+1))))
            for i in range(len(data)):
                h[hnamep].SetBinContent(i+1, data[i])
                for m in s['modifiers']:
                    if m['type'] == 'normfactor' and 'r_' in m['name']:
                        poi = s['name']
                    if 'prop' in m['name']:
                        h[hnamep].SetBinError(i+1, m['data'][i])
            h[hnamep].SetDirectory(sd)
            h[hnamep].Write()

        for obs in d['observations']:
            if obs['name'] == ch['name']:
                hname = 'data_obs'
                hnamep = ch['name']+'_'+hname
                data = obs['data']
                nb = len(data)
                h[hnamep] = ROOT.TH1F(hname, hname, nb, array('f', list(np.arange(nb+1))))
                for i in range(len(data)):
                    h[hnamep].SetBinContent(i+1, data[i])
                    h[hnamep].SetBinError(i+1, math.sqrt(data[i]))
                h[hnamep].SetDirectory(sd)
                h[hnamep].Write()
             
    fr.Close()
    
    # Create datacard
    chans = []
    for ch in d['channels']:
        chans.append(ch['name'])
    nchan = len(chans)
    sampord = [poi]
    for s in samp:
        if s == poi: continue
        sampord.append(s)
    samples = list(set(sampord))
    nsamp = len(samples)
    dc = 'imax '+str(nchan)+' number of bins\n'
    dc += 'jmax '+str(nsamp-1)+' number of processes minus 1\n'
    dc += 'kmax 0 number of nuisance parameters\n'
    dc += '------------------------------------\n'
    for ch in chans:
        dc += 'shapes * '+ch+' '+options.output.split('/')[-1]+'.root '+ch+'/$PROCESS '+ch+'/$PROCESS_$SYSTEMATIC\n'
    dc += '------------------------------------\n'
    dc += 'bin          '+' '.join(chans)+'\n'
    dc += 'observation  '+' '.join(np.repeat('-1 ', nchan))+'\n'
    dc += '------------------------------------\n'
    procbin, procname, procsamp, rate = [], [], [], []
    for ch in d['channels']:
        for i, s in enumerate(samples):
            procbin.append(ch['name'])
            procname.append(s)
            procsamp.append(str(i))
            rate.append(str(-1))
    dc += 'bin          '+' '.join(procbin)+'\n'
    dc += 'process      '+' '.join(procname)+'\n'
    dc += 'process      '+' '.join(procsamp)+'\n'
    dc += 'rate         '+' '.join(rate)+'\n'
    dc += '------------------------------------\n'
    for ch in chans:
        if bbl: dc += ch+' autoMCStats 0 1 1\n'
        else: dc += ch+' autoMCStats 0 100000 100000\n'
    with open(options.output+'.txt', 'w') as f:
        f.write(dc)
        f.close()