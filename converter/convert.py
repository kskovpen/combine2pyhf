#!/usr/bin/python3

import os, sys, glob

ws = os.environ['WS']

os.system('mkdir -p '+ws+'/validation/cards/combine; mkdir -p '+ws+'/validation/cards/pyhf')

# combine to pyhf
os.chdir(ws+'/validation/cards/pyhf')
fc = glob.glob(ws+'/cards/combine/*.txt')
for f in fc:
    os.system('python3 /HiggsAnalysis/CombinedLimit/test/datacardConvert.py '+f+' --out '+ws+'/cards/pyhf/'+os.path.splitext(f)[0])
    
# pyhf to combine
os.chdir(ws+'/validation/cards/combine')
fc = glob.glob(ws+'/cards/pyhf/*.txt')
for f in fc:
    os.system('python3 '+ws+'/convert/pyhf2combine.py --input '+f+' --output '+ws+'/cards/combine/'+os.path.splitext(f)[0])