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
        
    # Get nuiscances
    mods, nuis = {}, []
    for ch in d['channels']:
        for s in ch['samples']:
            for m in s['modifiers']:
                if m['name'] not in mods.keys():
                    mods[m['name']] = m
                    if 'r_' not in m['name'] and 'prop' not in m['name']: nuis.append(m['name'])                    
                    
    # Create shape file
    samp = []
    poi = []
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
            bins = array('f', list(np.arange(nb+1)))
            h[hnamep] = ROOT.TH1D(hname, hname, nb, bins)
            for m in s['modifiers']:
                if m['type'] in ['histosys']:
                    hsys = hnamep+'_'+m['name']
                    hsysname = hname+'_'+m['name']
                    hsysname = hsysname.replace('_splitns', '')
                    h[hsys+'Up'] = ROOT.TH1D(hsysname+'Up', hsysname+'Up', nb, bins)
                    h[hsys+'Down'] = ROOT.TH1D(hsysname+'Down', hsysname+'Down', nb, bins)                    
            for i in range(len(data)):
                h[hnamep].SetBinContent(i+1, data[i])
                for m in s['modifiers']:
                    if m['type'] == 'normfactor':
                        poi.append([s['name'], m['name'], ch['name']])
                    elif 'prop' in m['name'] or 'staterror' in m['type']:
                        h[hnamep].SetBinError(i+1, m['data'][i])
                    elif m['type'] in ['histosys']:
                        vup = m['data']['hi_data'][i]
                        vdown = m['data']['lo_data'][i]
                        hsys = hnamep+'_'+m['name']
                        if 'splitns' in m['name']:
                            for mn in s['modifiers']:
                                if mn['type'] == 'normsys' and mn['name'] == m['name']:
                                    vup *= mn['data']['hi']
                                    vdown *= mn['data']['lo']
                                    break
                        h[hsys+'Up'].SetBinContent(i+1, vup)
                        h[hsys+'Down'].SetBinContent(i+1, vdown)

        for hk in h.keys():
            h[hk].SetDirectory(sd)
            h[hk].Write()

        for obs in d['observations']:
            if obs['name'] == ch['name']:
                hname = 'data_obs'
                hnamep = ch['name']+'_'+hname
                data = obs['data']
                nb = len(data)
                h[hnamep] = ROOT.TH1D(hnamep, hnamep, nb, array('f', list(np.arange(nb+1))))
                for i in range(len(data)):
                    h[hnamep].SetBinContent(i+1, data[i])
                    h[hnamep].SetBinError(i+1, math.sqrt(data[i]))
                h[hnamep].SetDirectory(sd)
                h[hnamep].Write(hname)
             
    fr.Close()
    
    # Create datacard
    
    chans = []
    for ch in d['channels']:
        chans.append(ch['name'])
    nchan = len(chans)
    samples = list(set(samp))
    poisig = ''
    normf = []
    for p in poi:
        if 'r_' in p[1] or 'XS' in p[1]: poisig = p[0]
        else: normf.append(p)
    samples.remove(poisig)
    samples = [poisig]+samples
    nsamp = len(samples)
    dc = 'imax '+str(nchan)+' number of bins\n'
    dc += 'jmax '+str(nsamp-1)+' number of processes minus 1\n'
    dc += 'kmax '+str(len(nuis))+' number of nuisance parameters\n'
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
                    
    for m in mods.keys():
        s = mods[m]
        sysl = ''
        if s['type'] not in ['histosys', 'normsys']: continue
        if s['type'] == 'histosys':
            sysl += s['name'].replace('_splitns', '')+' shape '
            for ch in d['channels']:
                for samp in ch['samples']:
                    found = False
                    for sysn in samp['modifiers']:
                        if sysn['name'] == s['name']:
                            sysl += ' 1.0 '
                            found = True
                            break
                    if not found: sysl += ' - '
        elif s['type'] == 'normsys' and 'splitns' not in s['name']:
            sysl += s['name']+' lnN '
            for ch in d['channels']:
                for samp in ch['samples']:
                    found = False
                    for sysn in samp['modifiers']:
                        if sysn['name'] == s['name']:
                            sysl += ' '+str(sysn['data']['hi'])
                            found = True
                            break
                    if not found: sysl += ' - '
        if sysl != '':
            sysl += '\n'
            dc += sysl
            
    
    for p in normf:
        dc += p[1]+' rateParam '+p[0]+' '+p[2]+' 1 [0.,10.]\n'

    hasStat = False
    for m in mods.keys():
        if 'prop' in m or 'staterror' in mods[m]['type']:
            hasStat = True
            break
    if hasStat:
        dc += '------------------------------------\n'
        for ch in chans:
            if bbl: dc += ch+' autoMCStats 0 1 1\n'
            else: dc += ch+' autoMCStats 0 100000 100000\n'
            
    with open(options.output+'.txt', 'w') as f:
        f.write(dc)
        f.close()