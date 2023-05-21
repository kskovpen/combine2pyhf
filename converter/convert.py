#!/usr/bin/python3

import os, sys, glob

ws = os.environ['WS']
wd = ws+'/validation'

os.system('mkdir -p '+wd+'/cards/combine/combine2pyhf; mkdir -p '+wd+'/cards/combine/pyhf2combine')
os.system('mkdir -p '+wd+'/cards/pyhf/pyhf2combine; mkdir -p '+wd+'/cards/pyhf/combine2pyhf')

# combine cards
dc = glob.glob(ws+'/cards/combine/*')
for d in dc:
    os.system('mkdir '+wd+'/cards/combine/combine2pyhf/'+d)
    os.system('mkdir '+wd+'/cards/combine/pyhf2combine/'+d)
    fc = glob.glob(ws+'/cards/combine/'+d+'/*.txt')
    for f in fc:
        # combine -> pyhf
        os.system('python3 /HiggsAnalysis/CombinedLimit/test/datacardConvert.py '+f+' --out '+wd+'/cards/combine/combine2pyhf/'+d+'/'+os.path.splitext(f)[0])
        # pyhf -> combine
        os.system('python3 '+ws+'/convert/pyhf2combine.py --input '+wd+'/cards/combine/combine2pyhf/'+d+'/'+os.path.splitext(f)[0]+' --output '+wd+'/cards/combine/pyhf2combine/'+d+'/'+os.path.splitext(f)[0])
    
# pyhf cards
dc = glob.glob(ws+'/cards/pyhf/*.json')
for d in dc:
    os.system('mkdir '+wd+'/cards/pyhf/pyhf2combine/'+d)
    os.system('mkdir '+wd+'/cards/pyhf/combine2pyhf/'+d)
    fc = glob.glob(ws+'/cards/pyhf/'+d+'/*.json')
    for f in fc:
        # pyhf -> combine
        os.system('python3 '+ws+'/convert/pyhf2combine.py --input '+f+' --output '+wd+'/cards/pyhf/pyhf2combine/'+d+'/'+os.path.splitext(f)[0])
        # combine -> pyhf
        os.system('python3 /HiggsAnalysis/CombinedLimit/test/datacardConvert.py '+wd+'/cards/pyhf/pyhf2combine/'+d+'/'+os.path.splitext(f)[0]+' --out '+wd+'/cards/pyhf/combine2pyhf/'+d+'/'+os.path.splitext(f)[0])