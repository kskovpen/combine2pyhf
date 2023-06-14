#!/usr/bin/python3

import os, sys, math, json, logging, subprocess
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

def main(argv = None):
    
    if argv == None:
        argv = sys.argv[1:]
        
    usage = "usage: %prog [options]\n Run pyhf tests"
    
    parser = OptionParser(usage)
    
    (options, args) = parser.parse_args(sys.argv[1:])
    
    return options

if __name__ == '__main__':
    
    options = main()

    ws = os.environ['WS']
    indir = ws+'/validation/cards/pyhf/combine2pyhf'

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=ws+'/logs/pyhf.log',
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)
    
    logging.info('Start pyhf fits')
    pyhflog = logging.getLogger('fit.pyhf')
    
    dc = glob.glob(indir+'/*')
    
#    for d in dc:
#        dname = d.split('/')[-1]
#        os.chdir(indir+'/'+dname)
#        fc = glob.glob(indir+'/'+dname+'/*.txt')
#        for f in fc:
#            fname = f.replace('.txt', '')
#            comblog.info('--> Run fits ('+dname+')')
#            comblog.info('--> Prepare the workspace')
#            execute(comblog, 'text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:defaultModel -o '+fname+'_model.root '+f)
#            for fit in fits.keys():
#                comblog.info('--> Perform the best fit ('+fit+')')
#                execute(comblog, 'combine -M MultiDimFit '+fits[fit]+'--saveWorkspace --saveNLL --expectSignal=1 -n BestFit '+opts+' '+fname+'_model.root')
#                bf = postproc(comblog, 'higgsCombineBestFit.MultiDimFit.mH120.root')
#                bfnll = bf['nll']
#                comblog.info('    bf='+str(bf['r'])+', nll='+str(bfnll))
#                rs = [0.68, 0.84, 1, 1.16, 1.32]
#                comblog.info('--> Perform the scan ('+fit+')')
#                for r in rs:
#                    execute(comblog, 'combine -M MultiDimFit '+fits[fit]+'-d higgsCombineBestFit.MultiDimFit.mH120.root --saveNLL -w w --snapshotName \"MultiDimFit\" -n Fit_r'+str(r)+' '+opts+' --setParameters r='+str(r)+' --freezeParameters r')
#                    fres = postproc(comblog, 'higgsCombineFit_r'+str(r)+'.MultiDimFit.mH120.root')
#                    dnll = -2.*(fres['nll']-bfnll)
#                    comblog.info('    r='+str(fres['r'])+', dnll='+str(dnll))

