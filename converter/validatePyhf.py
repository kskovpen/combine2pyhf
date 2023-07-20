#!/usr/bin/python3

import os, sys, pyhf, json, glob, logging, subprocess
from deepdiff import DeepDiff

ws = os.environ['WS']
wd = ws+'/validation'
wdir = wd+'/cards/pyhf/combine2pyhf'

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=ws+'/logs/validatePyhf.log',
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
        forig = f.replace('validation/', '').replace('combine2pyhf/', '').replace('cards', 'combine2pyhf/combine2pyhf/cards')
        pyhflog.info('--> Compare json: '+os.path.splitext(forig.split('/')[-1])[0])
        with open(forig) as fforig:
            jorig = json.loads(fforig.read())
        with open(f) as ff:
            j = json.loads(ff.read())
        
        for ich, ch in enumerate(j['channels']):
            for isamp, s in enumerate(ch['samples']):
                for im, m in enumerate(s['modifiers']):
                    if 'splitns' in m['name'] and m['type'] == 'normsys':
                        for imm, mm in enumerate(s['modifiers']):
                            if m['name'] == mm['name'] and mm['type'] == 'histosys':
                                mods = j['channels'][ich]['samples'][isamp]['modifiers']
                                normsys = mods[im]
                                histosys = mods[imm]
                                for ib, b in enumerate(histosys['data']['hi_data']):
                                    histosys['data']['hi_data'][ib] *= normsys['data']['hi']
                                    histosys['data']['lo_data'][ib] *= normsys['data']['lo']
                                histosys['name'] = histosys['name'].replace('_splitns', '')
                                del mods[im]
                                break
            
        res = DeepDiff(jorig, j, significant_digits=15, ignore_order=True)
        if bool(res):
            pyhflog.error('--> Compare json: \033[1;31mfailed\x1b[0m')
            pyhflog.error(res)
        else:
            pyhflog.info('--> Compare json: \033[1;32mpassed\x1b[0m')