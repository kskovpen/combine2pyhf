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
            print(l)
            if 'imax 1 number of bins' in l:
                lines[il] = 'imax 2 number of bins\n'
                print('point1')
            elif 'shapes' in l:
                lines[il] += '\n '+l.replace('ch1', 'ch2')+'\n'
                print('point2')
            elif 'bin          ch1' == l:
                lines[il] = 'bin          ch1 ch2\n'
                print('point3')
            elif 'observation  -1' in l:
                lines[il] = 'observation  -1 -1\n'
                print('point4')
            elif 'bin          ch1 ch1' == l:
                lines[il] = 'bin          ch1 ch1 ch2 ch2\n'
                print('point5')
            elif 'process      sig bkg' == l:
                lines[il] = 'process      sig bkg sig bkg\n'
                print('point6')
            elif 'process      0 1' == l:
                lines[il] = 'process      0 1 0 1\n'
                print('point7')
            elif 'rate         -1 -1' == l:
                lines[il] = 'rate         -1 -1 -1 -1\n'
                print('point8')
            elif 'autoMCStats' in l:
                lines[il] += '\n '+l.replace('ch1', 'ch2')
                print('point9')
        with open(d.replace('one-bin', 'multi-bin'), 'w') as fw:
            for l in lines:
                fw.write(l)
            
# pyhf cards
dc = glob.glob(ws+'/cards/pyhf/one-bin/*.json')
for d in dc:
    res = json.load(open(d))
    res['channels'].append(res['channels'][0])
    res['channels'][-1]['name'] = "ch2"
    res['observations'].append(res['observations'][0])
    res['observations'][-1]['name'] = "ch2"
    json.dump(res, open(d.replace('one-bin', 'multi-bin'), 'w'), indent=2)