#!/usr/bin/python3

import os, sys, math, json, itertools
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
    
    # BB-lite check
    bbl = False
    for ch in d['channels']:
        for s in ch['samples']:
            for m in s['modifiers']:
                if 'prop' in m['name'] or m['type'] == 'staterror' or m['type'] == 'shapesys':
                    bbl = True
                    break
            if bbl: break
        if bbl: break
        
    # Get nuiscances
    mods, nuis, samples = {}, [], []
    for ch in d['channels']:
        for s in ch['samples']:
            if s['name'] not in samples:
                samples.append(s['name'])
            for m in s['modifiers']:
                if m['name'] not in mods.keys():
                    mods[m['name']] = m
                    if m['type'] not in ['normfactor', 'staterror', 'lumi'] and 'prop' not in m['name']: nuis.append(m['name'])
    nuis = [s.replace('_splitns', '') for i, s in enumerate(nuis)]
    nuis = list(set(nuis))
                    
    # Create shape file
    poi = []
    for ch in d['channels']:
        h = {}
        fr.cd()
        sd = fr.mkdir(ch['name']);
        sd.cd()
        for s in ch['samples']:
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
                        
        chsamp = [s['name'] for s in ch['samples']]
        for s in samples:
            if s not in chsamp:
                hname = s
                hnamep = ch['name']+'_'+s
                h[hnamep] = ROOT.TH1D(hname, hname, nb, bins)

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
    samples = []
    for ich, ch in enumerate(d['channels']):
        chans.append(ch['name'])
        if ich == 0:
            for samp in ch['samples']:
                samples.append(samp['name'])
    nchan = len(chans)
    poisig = ''
    normf = []
    for p in poi:
        if 'r_' in p[1] or 'XS' in p[1]: poisig = p[0]
        else: normf.append(p)
    samples.remove(poisig)
    samples = [poisig]+samples
    nsamp = len(set(samples))
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
    procbin, procname, procsamp, rate, samplenames = [], [], [], [], []
    for ich, ch in enumerate(d['channels']):
        for i, s in enumerate(samples):
            procbin.append(ch['name'])
            if ich == 0: samplenames.append(s)
            procname.append(s)
            procsamp.append(str(i))
            rate.append(str(-1))
    dc += 'bin          '+' '.join(procbin)+'\n'
    dc += 'process      '+' '.join(procname)+'\n'
    dc += 'process      '+' '.join(procsamp)+'\n'
    dc += 'rate         '+' '.join(rate)+'\n'
    dc += '------------------------------------\n'

    sysd = []
    for m in mods.keys():
        s = mods[m]
        sysl = ''
        if s['type'] not in ['histosys', 'normsys']: continue
        sname = s['name'].replace('_splitns', '')
        if sname in sysd: continue
        if s['type'] == 'histosys':
            sysl += sname+' shape '
            for ch in d['channels']:
                for samp in ch['samples']:
                    found = False
                    for sysn in samp['modifiers']:
                        if sysn['name'].replace('_splitns', '') == sname:
                            sysl += ' 1.0 '
                            found = True
                            break
                    if not found: sysl += ' - '
        elif s['type'] == 'normsys' and 'splitns' not in s['name']:
            sysl += s['name']+' lnN '
            for ch in d['channels']:
                for samp in samplenames:                    
                    found = False
                    for sa in ch['samples']:
                        if sa['name'] == samp:
                            for sysn in sa['modifiers']:
                                if sysn['name'] == s['name']:
                                    if abs(sysn['data']['lo']-1./sysn['data']['hi']) < 1E-5:
                                        sysl += ' '+str(sysn['data']['hi'])
                                    else:
                                        sysl += ' '+str(sysn['data']['hi'])+'/'+str(sysn['data']['lo'])                                        
                                    found = True
                                    break
                    if not found: sysl += ' - '
        if sysl != '':
            sysl += '\n'
            dc += sysl
            sysd.append(sname)
            
    normf.sort()
    normf = list(k for k, _ in itertools.groupby(normf))
    for p in normf:
        dc += p[1]+' rateParam '+p[2]+' '+p[0]+' 1 [0.,10.]\n'

    hasStat = False
    for m in mods.keys():
        if 'prop' in m or 'staterror' in mods[m]['type']:
            hasStat = True
            break
    dc += '------------------------------------\n'
    for ch in chans:
        if hasStat:
            if bbl: dc += ch+' autoMCStats 0 1 2\n'
            else: dc += ch+' autoMCStats 0 100000 2\n'
        else: dc += ch+' autoMCStats -1 1 2\n'
            
    with open(options.output+'.txt', 'w') as f:
        f.write(dc)
        f.close()