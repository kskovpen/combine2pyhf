import os, sys, math, json, glob, logging, subprocess
from timeit import default_timer as timer
import utils
from optparse import OptionParser
import ROOT
        
def postproc(logger, fname, bf = None, fdir = '', fit = '', fout = ''):
    try:
        return getFitInfo(fname, bf, fdir, fit, fout)
    except Exception as e:
        logger.error(e)
        
def getFitInfo(fname, bf = None, fdir = '', fit = '', fout = ''):
    f = ROOT.TFile(fname, 'READ')
    tr = f.Get('limit')
    res = {'r': [], 'nll': []}
    for i in range(tr.GetEntries()):
        tr.GetEntry(i)
        if tr.r in res['r']: continue
        res['r'].append(tr.r)
        res['nll'].append(2*(tr.nll0+tr.nll+tr.deltaNLL))
    if bf: 
        res['bf'] = [bf['r'][0]]
        res['time'] = bf['time']
        utils.setprec(res['bf'], prec=6)
        utils.setprec(res['r'])
    utils.setprec(res['nll'], prec=6)
    if fout != '':
        os.system('mkdir -p '+fdir+'/'+fout)
        json.dump(res, open(fdir+'/'+fout+'/'+fit+'_combine.json', 'w'), indent=2)
    return res

def main(argv = None):
    
    if argv == None:
        argv = sys.argv[1:]
        
    usage = "usage: %prog [options]\n Run combine tests"
    
    parser = OptionParser(usage)
    parser.add_option("--npoints", default=50, type=int, help="Number of points to scan [default: %default]")
    parser.add_option("--min", default=0.5, type=float, help="Scan range min value [default: %default]")
    parser.add_option("--max", default=1.5, type=float, help="Scan range max value [default: %default]")
    
    (options, args) = parser.parse_args(sys.argv[1:])
    
    return options

if __name__ == '__main__':
    
    options = main()

    ws = os.environ['WS']
    wd = ws+'/validation'
    indir = wd+'/cards/combine/pyhf2combine'

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
            comblog.info('--> Run fits ('+dname+', '+fname.split('/')[-1]+')')
            comblog.info('--> Prepare the workspace')
            utils.execute(comblog, 'text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:defaultModel -o '+fname+'_model.root '+f)
            for fit in fits.keys():
                comblog.info('--> Perform the best fit ('+fit+')')
                start = timer()
                comblog.info('combine -M MultiDimFit '+fits[fit]+'--saveWorkspace --saveNLL --expectSignal=1 -n BestFit '+opts+' '+fname+'_model.root')
                utils.execute(comblog, 'combine -M MultiDimFit '+fits[fit]+'--saveWorkspace --saveNLL --expectSignal=1 -n BestFit '+opts+' '+fname+'_model.root')
                end = timer()
                fittime = end-start
                bfres = postproc(comblog, 'higgsCombineBestFit.MultiDimFit.mH120.root')
                bfres['time'] = fittime
                comblog.info('    bf='+str(bfres['r'][0]))
                comblog.info('--> Perform the scan ('+fit+')')
                comblog.info('combine -M MultiDimFit '+fits[fit]+'-d higgsCombineBestFit.MultiDimFit.mH120.root --saveNLL -w w --snapshotName \"MultiDimFit\" -n Scan '+opts+' --algo grid --rMin '+str(options.min)+' --rMax '+str(options.max)+' --points '+str(options.npoints+1)+' --freezeParameters r --setParameters r=1 --alignEdges 1')
                utils.execute(comblog, 'combine -M MultiDimFit '+fits[fit]+'-d higgsCombineBestFit.MultiDimFit.mH120.root --saveNLL -w w --snapshotName \"MultiDimFit\" -n Scan '+opts+' --algo grid --rMin '+str(options.min)+' --rMax '+str(options.max)+' --points '+str(options.npoints+1)+' --freezeParameters r --setParameters r=1 --alignEdges 1')
                fres = postproc(comblog, 'higgsCombineScan.MultiDimFit.mH120.root', bfres, ws+'/results', fit, fname.split('/')[-1])
                for i in range(len(fres['r'])):
                    comblog.info('    r='+str(fres['r'][i])+', delta_nll='+str(fres['nll'][i]))

