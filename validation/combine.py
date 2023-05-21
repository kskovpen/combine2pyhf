#!/usr/bin/python3

import os, sys, math, json, glob
from optparse import OptionParser
import ROOT

def main(argv = None):
    
    if argv == None:
        argv = sys.argv[1:]
        
    usage = "usage: %prog [options]\n Run combine tests"
    
    parser = OptionParser(usage)
    
    (options, args) = parser.parse_args(sys.argv[1:])
    
    return options

if __name__ == '__main__':
    
    options = main()
    
    indir = os.environ['WS']+'/validation/cards/combine/pyhf2combine'
    dc = glob.glob(indir+'/*')
    
    for d in dc:
        dname = d.split('/')[-1]
        outdir = os.environ['WS']+'/validation/results/combine/'+dname
        os.system('mkdir -p '+outdir)
        fc = glob.glob(indir+'/'+dname+'/*.txt')
        for f in fc:
            fname = f.replace('.txt', '')
            # do not use analytical minimization (not implemented in pyhf); store the full nll
            opts = '--X-rtd REMOVE_CONSTANT_ZERO_POINT=1 --X-rtd MINIMIZER_no_analytic'
            os.system('text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:defaultModel -o '+outdir+'/'+fname+'_model.root '+f)
            os.system('combine -M MultiDimFit -t -1 --saveWorkspace --expectSignal=1 '+opts+' '+outdir+'/'+fname+'_model.root')
            # for r in [0.68, 0.84, 1, 1.16, 1.32]:
