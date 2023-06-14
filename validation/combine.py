#!/usr/bin/python3

import os, sys, math, json, glob, logging, subprocess
from optparse import OptionParser
import ROOT

def execute(logger, c):
    try:
        r = subprocess.check_output(c, stderr=subprocess.STDOUT, shell=True)
        logger.debug(r)
    except subprocess.CalledProcessError as e:
        logger.error(e.output)
        
def postproc(logger, fname):
    try:
        getFitInfo(fname)
    except Exception as e:
        logger.error(e)
        
def getFitInfo(fname):
    f = ROOT.TFile(fname, 'READ')
    tr = f.Get('limit')
    res = {'r': None, 'deltaNLL': None, 'nll': None, 'nll0': None}
    tr.GetEntry(0)
    res['r'] = tr.r
    res['deltaNLL'] = 2.*tr.deltaNLL
    res['nll'] = tr.nll
    res['nll0'] = tr.nll0
    json.dump(res, open(fname.replace('.root', '.json'), 'w'), indent=2)
    return res

def main(argv = None):
    
    if argv == None:
        argv = sys.argv[1:]
        
    usage = "usage: %prog [options]\n Run combine tests"
    
    parser = OptionParser(usage)
    
    (options, args) = parser.parse_args(sys.argv[1:])
    
    return options

if __name__ == '__main__':
    
    options = main()

    ws = os.environ['WS']
    indir = ws+'/validation/cards/combine/pyhf2combine'

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=ws+'/logs/combine.log',
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)
    
    logging.info('Start combine fits')
    comblog = logging.getLogger('fit.combine')
    
    dc = glob.glob(indir+'/*')
    
    fits = {'asi': '-t -1 ', 'obs': ''}
    
    # do not use analytical minimization (pyhf does not use it); store the full nll
    opts = '--X-rtd REMOVE_CONSTANT_ZERO_POINT=1 --X-rtd MINIMIZER_no_analytic'
    
    for d in dc:
        dname = d.split('/')[-1]
        os.chdir(indir+'/'+dname)
        fc = glob.glob(indir+'/'+dname+'/*.txt')
        for f in fc:
            fname = f.replace('.txt', '')
            comblog.info('--> Run fits ('+dname+')')
            comblog.info('--> Prepare the workspace')
            execute(comblog, 'text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:defaultModel -o '+fname+'_model.root '+f)
            for fit in fits.keys():
                # get the best-fit snapshot
                comblog.info('--> Perform the best fit ('+fit+')')
                execute(comblog, 'combine -M MultiDimFit '+fits[fit]+'--saveWorkspace --saveNLL --expectSignal=1 -n BestFit '+opts+' '+fname+'_model.root')
                execute(comblog, 'ls')
                bf = postproc(comblog, getFitInfo('higgsCombineBestFit.MultiDimFit.mH120.root'))
#                comblog.info('bf='+str(bf['r'])+', nll='+str(bf['nll']))
                # perform a NLL scan
#                rs = [0.68, 0.84, 1, 1.16, 1.32]
#                for r in rs:
#                    comblog.info('--> Perform the fit for r='+str(r)+' ('+fit+')')
#                    execute(comblog, 'combine -M MultiDimFit '+fits[fit]+'-d higgsCombineBestFit.MultiDimFit.mH120.root --saveNLL -w w --snapshotName \"MultiDimFit\" -n Fit_r'+str(r)+' --setParameters r='+str(r)+' --freezeParameters r')
#                    fres = postproc(comblog, getFitInfo('higgsCombineFit_r'+str(r)+'.MultiDimFit.mH120.root'))
#                    comblog.info('rf='+str(fres['r'])+', deltaNLL='+str(fres['nll']))

