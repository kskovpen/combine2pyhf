#!/usr/bin/python3

import os, sys, glob, ROOT

ws = os.environ['WS']
wd = ws+'/validation'

def shapeloc(dname, fname, combine2pyhf = False):
    with open(fname+'_mod', 'w') as f:
        with open(fname, 'r') as fr:
            for line in fr:
                if '.root' in line:
                    words = line.split()
                    for i, w in enumerate(words):
                        if '.root' in w:
                            if combine2pyhf: words[i] = wd+'/cards/combine/combine2pyhf/'+dname+'/'+w
                            else: words[i] = wd+'/cards/combine/pyhf2combine/'+dname+'/'+w
                    f.write(' '.join(words)+'\n')
                else: f.write(line)
    os.system('mv '+fname+'_mod '+fname)

# combine cards
dc = glob.glob(ws+'/cards/combine/*')
for d in dc:
    dname = d.split('/')[-1]
    print('Convert '+dname+' (combine)')
    os.system('mkdir -p '+wd+'/cards/combine/combine2pyhf/'+dname)
    os.system('mkdir -p '+wd+'/cards/combine/pyhf2combine/'+dname)
    os.system('cp '+ws+'/cards/combine/'+dname+'/* '+wd+'/cards/combine/combine2pyhf/'+dname+'/.')
    fc = glob.glob(wd+'/cards/combine/combine2pyhf/'+dname+'/*.txt')
    for f in fc:
        fname = f.split('/')[-1]
        shapeloc(dname, f, combine2pyhf = True)
        with open(wd+'/cards/combine/combine2pyhf/'+dname+'/'+os.path.splitext(fname)[0]+'.txt', 'r') as ff:
            lines = ff.readlines()
            for l in lines:
                print(l)
        print('combine -> pyhf: '+fname)
        os.system('python3 /HiggsAnalysis/CombinedLimit/test/datacardConvert.py '+f+' --out '+wd+'/cards/combine/combine2pyhf/'+dname+'/'+os.path.splitext(fname)[0])
        print('pyhf -> combine: '+fname)
        os.system('python3 '+ws+'/converter/pyhf2combine.py --input '+wd+'/cards/combine/combine2pyhf/'+dname+'/'+fname.replace('.txt', '.json')+' --output '+wd+'/cards/combine/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0])
    
# pyhf cards
dc = glob.glob(ws+'/cards/pyhf/*')
for d in dc:
    dname = d.split('/')[-1]
    print('Convert '+dname+' (pyhf)')
    os.system('mkdir -p '+wd+'/cards/pyhf/pyhf2combine/'+dname)
    os.system('mkdir -p '+wd+'/cards/pyhf/combine2pyhf/'+dname)
    os.system('cp '+ws+'/cards/combine/'+dname+'/* '+wd+'/cards/combine/pyhf2combine/'+dname+'/.')
    fc = glob.glob(wd+'/cards/pyhf/pyhf2combine/'+dname+'/*.json')
    for f in fc:
        fname = f.split('/')[-1]
        print('pyhf -> combine: '+fname)
        os.system('python3 '+ws+'/converter/pyhf2combine.py --input '+f+' --output '+wd+'/cards/pyhf/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0])
        froot = wd+'/cards/pyhf/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0]+'.root'
        print('combine -> pyhf: '+fname)
        shapeloc('pyhf/pyhf2combine/'+dname, wd+'/cards/pyhf/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0]+'.txt')
#        with open(wd+'/cards/pyhf/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0]+'.txt', 'r') as ff:
#            lines = ff.readlines()
#            for l in lines:
#                print(l)
        os.system('python3 /HiggsAnalysis/CombinedLimit/test/datacardConvert.py '+wd+'/cards/pyhf/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0]+'.txt  --out '+wd+'/cards/pyhf/combine2pyhf/'+dname+'/'+os.path.splitext(fname)[0])