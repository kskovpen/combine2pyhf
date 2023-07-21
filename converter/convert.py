#!/usr/bin/python3

import os, sys, glob, logging, subprocess, ROOT

ws = os.environ['WS']
wd = ws+'/validation'

sys.path.append(wd)
import utils

os.system('mkdir -p '+wd+'/cards/combine')
os.system('mkdir -p '+wd+'/cards/pyhf')

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=ws+'/logs/convert.log',
                    filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

logging.info('Start conversion process')
        
def shapeloc(dname, fname, tool = 'combine', combine2pyhf = False):
    with open(fname+'_mod', 'w') as f:
        with open(fname, 'r') as fr:
            for line in fr:
                if '.root' in line:
                    words = line.split()
                    for i, w in enumerate(words):
                        if '.root' in w:
                            if combine2pyhf: words[i] = wd+'/cards/'+tool+'/combine2pyhf/'+dname+'/'+w
                            else: words[i] = wd+'/cards/'+tool+'/pyhf2combine/'+dname+'/'+w
                    f.write(' '.join(words)+'\n')
                else: f.write(line)
    os.system('mv '+fname+'_mod '+fname)
   
def execshapeloc(logger, dname, fname, tool = 'combine', combine2pyhf = False):
    try:
        shapeloc(dname, fname, tool, combine2pyhf)
    except Exception as e:
        logger.error(e)

# combine cards
comblog = logging.getLogger('convert.combine')
dc = glob.glob(ws+'/cards/combine/*')
for d in dc:
    dname = d.split('/')[-1]
    comblog.info('Convert '+dname+' (combine)')
    os.system('mkdir -p '+wd+'/cards/combine/combine2pyhf/'+dname)
    os.system('mkdir -p '+wd+'/cards/combine/pyhf2combine/'+dname)
    os.system('cp '+ws+'/cards/combine/'+dname+'/* '+wd+'/cards/combine/combine2pyhf/'+dname+'/.')
    fc = glob.glob(wd+'/cards/combine/combine2pyhf/'+dname+'/*.txt')
    for f in fc:
        fname = f.split('/')[-1]
        os.system('mkdir -p '+ws+'/results/combine/'+os.path.splitext(fname)[0])
        bbl = '--bbl ' if 'bbl' in fname or 'cms-' in fname else ''
        execshapeloc(comblog, dname, f, tool = 'combine', combine2pyhf = True)
        comblog.info('combine -> pyhf: '+fname)
        utils.execute(comblog, 'python3 /HiggsAnalysis/CombinedLimit/test/datacardConvert.py '+bbl+f+' --normshape --out '+wd+'/cards/combine/combine2pyhf/'+dname+'/'+os.path.splitext(fname)[0])
        comblog.info('combine -> pyhf: plot distributions')
        utils.execute(comblog, 'python3 '+ws+'/converter/hist.py --input '+wd+'/cards/combine/combine2pyhf/'+dname+'/'+fname.replace('.txt', '.json')+' --output '+ws+'/results/combine/'+os.path.splitext(fname)[0]+'/hist')
        comblog.info('pyhf -> combine: '+fname)
        utils.execute(comblog, 'python3 '+ws+'/converter/pyhf2combine.py --normshape --input '+wd+'/cards/combine/combine2pyhf/'+dname+'/'+fname.replace('.txt', '.json')+' --output '+wd+'/cards/combine/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0])
        execshapeloc(comblog, dname, wd+'/cards/combine/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0]+'.txt')
        
#        frr = ROOT.TFile((wd+'/cards/combine/combine2pyhf/'+dname+'/'+os.path.splitext(fname)[0])+'.root', 'READ')
#        keyso = frr.GetDirectory('ch1').GetListOfKeys()
#        print(keyso)
#        for k in keyso:
#            hp = k.ReadObj()
#            print(hp.GetName(), hp.Print("all"))
#        frr.Close()
    
# pyhf cards
pyhflog = logging.getLogger('convert.pyhf')
dc = glob.glob(ws+'/cards/pyhf/*')
for d in dc:
    dname = d.split('/')[-1]
    pyhflog.info('Convert '+dname+' (pyhf)')
    os.system('mkdir -p '+wd+'/cards/pyhf/pyhf2combine/'+dname)
    os.system('mkdir -p '+wd+'/cards/pyhf/combine2pyhf/'+dname)
    os.system('cp '+ws+'/cards/pyhf/'+dname+'/* '+wd+'/cards/pyhf/pyhf2combine/'+dname+'/.')
    fc = glob.glob(wd+'/cards/pyhf/pyhf2combine/'+dname+'/*.json')
    for f in fc:
        fname = f.split('/')[-1]
        os.system('mkdir -p '+ws+'/results/pyhf/'+os.path.splitext(fname)[0])
        bbl = '--bbl ' if 'bbl' in fname or 'atlas-' in fname else ''
        pyhflog.info('pyhf -> combine: '+fname)
        utils.execute(pyhflog, 'python3 '+ws+'/converter/pyhf2combine.py --input '+f+' --output '+wd+'/cards/pyhf/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0])
        froot = wd+'/cards/pyhf/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0]+'.root'
        pyhflog.info('combine -> pyhf: '+fname)
        execshapeloc(pyhflog, dname, wd+'/cards/pyhf/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0]+'.txt', tool = 'pyhf')
        pyhflog.info('combine -> pyhf: plot distributions')
        utils.execute(pyhflog, 'python3 '+ws+'/converter/hist.py --input '+f+' --output '+ws+'/results/pyhf/'+os.path.splitext(fname)[0]+'/hist')
#        with open(wd+'/cards/pyhf/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0]+'.txt', 'r') as ff:
#            lines = ff.readlines()
#            for l in lines:
#                print(l)
        utils.execute(pyhflog, 'python3 /HiggsAnalysis/CombinedLimit/test/datacardConvert.py '+bbl+wd+'/cards/pyhf/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0]+'.txt --out '+wd+'/cards/pyhf/combine2pyhf/'+dname+'/'+os.path.splitext(fname)[0])