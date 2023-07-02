#!/usr/bin/python3

import os, sys, glob, ROOT, subprocess, json

ws = os.environ['WS']
wd = ws+'/validation'

sys.path.append(wd)
import utils

os.system('mkdir -p '+ws+'/cards/combine/multi-bin')
os.system('mkdir -p '+ws+'/cards/pyhf/multi-bin')

# combine cards
ro = glob.glob(ws+'/cards/combine/one-bin/*.root')
for r in ro:
    os.system('cp '+r+' '+ws+'/cards/combine/multi-bin/.')
dc = glob.glob(ws+'/cards/combine/one-bin/*.txt')
for d in dc:
    with open(d, 'r') as fr:
        lines = fr.readlines()
        for il, l in enumerate(lines):
            if 'imax 1 number of bins' in l:
                lines[il] = 'imax 2 number of bins\n'
            elif 'shapes' in l:
                lines[il] += '\n '+l.replace('ch1', 'ch2')+'\n'
            elif 'bin          ch1' == l:
                lines[il] = 'bin          ch1 ch2\n'
            elif 'observation  -1' in l:
                lines[il] = 'observation  -1 -1\n'
            elif 'bin          ch1 ch1' == l:
                lines[il] = 'bin          ch1 ch1 ch2 ch2\n'
            elif 'process      sig bkg' == l:
                lines[il] = 'process      sig bkg sig bkg\n'
            elif 'process      0 1' == l:
                lines[il] = 'process      0 1 0 1\n'
            elif 'rate         -1 -1' == l:
                lines[il] = 'rate         -1 -1 -1 -1\n'
            elif 'autoMCStats' in l:
                lines[il] += '\n '+l.replace('ch1', 'ch2')
        with open(d.replace('one-bin', 'multi-bin'), 'w') as fw:
            fw.write(lines)
            
# pyhf cards
dc = glob.glob(ws+'/cards/pyhf/one-bin/*.json')
for d in dc:
    res = json.load(open(d))
    res['channels'].append(res['channels'][0])
    res['channels'][-1]['name'] = "ch2"
    res['observations'].append(res['observations'][0])
    res['observations'][-1]['name'] = "ch2"
    json.dump(res, open(d.replace('one-bin', 'multi-bin'), 'w'), indent=2)