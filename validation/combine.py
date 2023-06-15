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
        return getFitInfo(fname)
    except Exception as e:
        logger.error(e)
        
def getFitInfo(fname):
    f = ROOT.TFile(fname, 'READ')
    tr = f.Get('limit')
    res = {'r': None, 'nll': None}
    for i in range(tr.GetEntries()):
        tr.GetEntry(i)
        res['r'].append(tr.r)
        res['nll'].append(2*(tr.nll0+tr.nll+tr.deltaNLL))
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
                comblog.info('--> Perform the best fit ('+fit+')')
                execute(comblog, 'combine -M MultiDimFit '+fits[fit]+'--saveWorkspace --saveNLL --expectSignal=1 -n BestFit '+opts+' '+fname+'_model.root')
                bf = postproc(comblog, 'higgsCombineBestFit.MultiDimFit.mH120.root')
                comblog.info('    bf='+str(bf['r'][0]))
                comblog.info('--> Perform the scan ('+fit+')')
                execute(comblog, 'combine -M MultiDimFit '+fits[fit]+'-d higgsCombineBestFit.MultiDimFit.mH120.root --saveNLL -w w --snapshotName \"MultiDimFit\" -n Scan '+opts+' --algo grid --rMin 0.6 --rMax 1.4 --points 5 --freezeParameters r')
                fres = postproc(comblog, 'higgsCombineScan.MultiDimFit.mH120.root')
                for i in range(len(fres['r'])):
                    comblog.info('    r='+str(fres['r'][i])+', delta_nll='+str(fres['nll'][i]))

