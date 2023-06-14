#!/usr/bin/python3

import os, sys, glob, ROOT, logging, subprocess

ws = os.environ['WS']
wd = ws+'/validation'

os.system('mkdir -p '+wd+'/cards/combine')
os.system('mkdir -p '+wd+'/cards/pyhf')

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=wd+'/cards/combine/convert.log',
                    filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

logging.info('Start conversion process')

def execute(logger, c):
    try:
        subprocess.check_output(c, shell=True)
    except subprocess.CalledProcessError as e:
        logger.error(e.output)
        
def shapeloc(dname, fname, combine2pyhf = False):
    with open(fname+'_mod', 'w') as f:
        with open(fname, 'r') as fr:
            for line in fr:
                if '.root' in line:
                    words = line.split()
                    for i, w in enumerate(words):
                        if '.root' in w:
                            if combine2pyhf: words[i] = wd+'/cards/combine/combine2pyhf/'+dname+'/'+w
                            else: words[i] = wd+'/sdfsdfcards/combine/pyhf2combine/'+dname+'/'+w
                    f.write(' '.join(words)+'\n')
                else: f.write(line)
    os.system('mv '+fname+'_mod '+fname)
   
def execshapeloc(logger, dname, fname, combine2pyhf = False):
    try:
        shapeloc(dname, fname, combine2pyhf)
    except Exception as e:
        logger.error(e.output)

comblog = logging.getLogger('convert.combine')
# combine cards
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
        execshapeloc(comblog, dname, f, combine2pyhf = True)
        comblog.info('combine -> pyhf: '+fname)
        execute(comblog, 'python3 /HiggsAnalysis/CombinedLimit/test/datacardConvert.py '+f+' --out '+wd+'/cards/combine/combine2pyhf/'+dname+'/'+os.path.splitext(fname)[0])
        comblog.info('pyhf -> combine: '+fname)
        execute(comblog, 'python3 '+ws+'/converter/pyhf2combine.py --input '+wd+'/cards/combine/combine2pyhf/'+dname+'/'+fname.replace('.txt', '.json')+' --output '+wd+'/cards/combine/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0])
        execshapeloc(comblog, dname, wd+'/cards/combine/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0]+'.txt')
    
# pyhf cards
#dc = glob.glob(ws+'/cards/pyhf/*')
#for d in dc:
#    dname = d.split('/')[-1]
#    print('Convert '+dname+' (pyhf)')
#    os.system('mkdir -p '+wd+'/cards/pyhf/pyhf2combine/'+dname)
#    os.system('mkdir -p '+wd+'/cards/pyhf/combine2pyhf/'+dname)
#    os.system('cp '+ws+'/cards/pyhf/'+dname+'/* '+wd+'/cards/pyhf/pyhf2combine/'+dname+'/.')
#    fc = glob.glob(wd+'/cards/pyhf/pyhf2combine/'+dname+'/*.json')
#    for f in fc:
#        fname = f.split('/')[-1]
#        print('pyhf -> combine: '+fname)
#        os.system('python3 '+ws+'/converter/pyhf2combine.py --input '+f+' --output '+wd+'/cards/pyhf/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0])
#        froot = wd+'/cards/pyhf/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0]+'.root'
#        print('combine -> pyhf: '+fname)
#        shapeloc('pyhf/pyhf2combine/'+dname, wd+'/cards/pyhf/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0]+'.txt')
##        with open(wd+'/cards/pyhf/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0]+'.txt', 'r') as ff:
##            lines = ff.readlines()
##            for l in lines:
##                print(l)
#        os.system('python3 /HiggsAnalysis/CombinedLimit/test/datacardConvert.py '+wd+'/cards/pyhf/pyhf2combine/'+dname+'/'+os.path.splitext(fname)[0]+'.txt  --out '+wd+'/cards/pyhf/combine2pyhf/'+dname+'/'+os.path.splitext(fname)[0])