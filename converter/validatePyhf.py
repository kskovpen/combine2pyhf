#!/usr/bin/python3

import os, sys, pyhf, json, glob, logging, subprocess, pydash
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
#                                for ib, b in enumerate(histosys['data']['hi_data']):
#                                    histosys['data']['hi_data'][ib] *= normsys['data']['hi']
#                                    histosys['data']['lo_data'][ib] *= normsys['data']['lo']
#                                histosys['name'] = histosys['name'].replace('_splitns', '')
                                del mods[im]
                                break
            
        res = DeepDiff(jorig, j, significant_digits=2, ignore_order=True, view='tree', verbose_level=1)
        passComp = True
        if bool(res):
            for pk in res.keys():
                if pk not in ['values_changed']: continue
                diffs = list(res[pk])
                for v in diffs:
                    r = v.path(output_format='list')
                    if 'measurements' in r: continue
                    d1 = pydash.get(jorig, r)
                    chName = d1['name']
                    d2 = pydash.get(j, r)

                    if 'samples' not in d1.keys(): continue
                    for s1 in d1['samples']:
                        for s2 in d2['samples']:
                            if s1['name'] == s2['name']:
                                nbins = len(s1['data'])
                                for ib in range(nbins):
                                    if s1['data'][ib] != s2['data'][ib]:
                                        pyhflog.error('Different data found')
                                        passComp = False
                                mods1 = [s['name'] for s in s1['modifiers'] if s['type'] not in ['shapesys', 'staterror', 'lumi'] and 'r_' not in s['name'] and 'XS' not in s['name'] and 'mu_tttt' not in s['name']]
                                mods2 = [s['name'] for s in s2['modifiers'] if s['type'] not in ['shapesys', 'staterror', 'lumi'] and 'r_' not in s['name'] and 'XS' not in s['name'] and 'mu_tttt' not in s['name']]
                                d = list(set(mods1) - set(mods2))
                                if len(d) > 0: 
                                    pyhflog.error('Different number of modifiers found')
                                    passComp = False
                                for mname in mods1:
                                    for im1, m1 in enumerate(s1['modifiers']):
                                        if m1['name'] != mname: continue
                                        for im2, m2 in enumerate(s2['modifiers']):
                                            if m2['name'] != mname: continue
                                            md1 = s1['modifiers'][im1]['data']
                                            md2 = s2['modifiers'][im2]['data']
                                            if type(md1) == dict:
                                                diff = DeepDiff(md1, md2, significant_digits=2, ignore_order=True)
                                                if diff:
                                                    pyhflog.error('Differences in modifiers found')
                                                    passComp = False
                                            break
                
        if not passComp:
            pyhflog.error('--> Compare json: \033[1;31mfailed\x1b[0m')
            pyhflog.error(res)
        else:
            pyhflog.info('--> Compare json: \033[1;32mpassed\x1b[0m')