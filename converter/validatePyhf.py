#!/usr/bin/python3

import os, sys, pyhf, json, glob, logging, subprocess

ws = os.environ['WS']
wd = ws+'/validation'
wdir = wd+'/cards/pyhf/combine2pyhf'

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=wd+'/cards/combine/validatePyhf.log',
                    filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

logging.info('Start validation process for pyhf json conversion')
pyhflog = logging.getLogger('convert.pyhf.validate')

runs = glob.glob(wdir+'/*/')
for r in runs:
    runName = r.split('/')[-2]
    fcv = glob.glob(wdir+'/'+runName+'/*.json')
    pyhflog.info('Validate '+runName+' (pyhf)')
    
    for f in fcv:
        forig = f.replace('validation/', '').replace('combine2pyhf/', '')
        pyhflog.info('Compare '+forig+' and '+f)