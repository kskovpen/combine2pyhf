#!/usr/bin/python3

import os, sys, glob

ws = os.environ['WS']
wd = ws+'/validation'

# combine cards
dc = glob.glob(ws+'/cards/combine/*')

def shapeloc(dname, fname):
    print('modify '+fname)
    with open(fname+'_mod', 'w') as f:
        with open(fname, 'r') as fr:
            for line in fr:
                if '.root' in line:
                    words = line.split()
                    for i, w in enumerate(words):
                        if '.root' in w:
                            print('old: '+' '.join(words))
                            words[i] = wd+'/cards/'+dname+'/'+w
                            print('new: '+' '.join(words))
                    f.write(' '.join(words)+'\n')
                else: f.write(line)
    os.system('mv '+fname+'_mod '+fname)

#for d in dc:
#    dname = d.split('/')[-1]
#    print('Convert '+dname+' (combine)')
#    os.system('mkdir -p '+wd+'/cards/combine/combine2pyhf/'+dname)
#    os.system('mkdir -p '+wd+'/cards/combine/pyhf2combine/'+dname)
#    fc = glob.glob(ws+'/cards/combine/'+dname+'/*.txt')
#    for f in fc:        
#        fname = f.split('/')[-1]
#        shapeloc(dname, f)
#        print('combine -> pyhf: '+fname)
#        os.system('python3 /HiggsAnalysis/CombinedLimit/test/datacardConvert.py '+f+' --out '+wd+'/cards/combine/combine2pyhf/'+dname+'/'+os.path.splitext(fname)[0])
#        print('pyhf -> combine: '+fname)
#        os.system('python3 '+ws+'/converter/pyhf2combine.py --input '+wd+'/cards/combine/combine2pyhf/'+dname+'/'+fname.replace('.txt', '.json')+' --output '+wd+'/cards/combine/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0])

    
# pyhf cards
dc = glob.glob(ws+'/cards/pyhf/*')
for d in dc:
    dname = d.split('/')[-1]
    print('Convert '+dname+' (pyhf)')
    os.system('mkdir -p '+wd+'/cards/pyhf/pyhf2combine/'+dname)
    os.system('mkdir -p '+wd+'/cards/pyhf/combine2pyhf/'+dname)
    fc = glob.glob(ws+'/cards/pyhf/'+dname+'/*.json')
    for f in fc:
        fname = f.split('/')[-1]
        print('pyhf -> combine: '+fname)
        print('output: '+wd+'/cards/pyhf/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0])
        os.system('python3 '+ws+'/converter/pyhf2combine.py --input '+f+' --output '+wd+'/cards/pyhf/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0])
        print('combine -> pyhf: '+fname)
        shapeloc('pyhf/pyhf2combine/'+dname, wd+'/cards/pyhf/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0]+'.txt')
        with open(wd+'/cards/pyhf/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0]+'.txt', 'r') as ff:
            lines = ff.readlines()
            for l in lines:
                print(l)
        os.system('python3 /HiggsAnalysis/CombinedLimit/test/datacardConvert.py '+wd+'/cards/pyhf/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0]+'.txt  --out '+wd+'/cards/pyhf/combine2pyhf/'+dname+'/'+os.path.splitext(fname)[0])