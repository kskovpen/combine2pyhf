import os, sys, math, json, glob, logging, subprocess, pyhf, iminuit
from timeit import default_timer as timer
import utils
import numpy as np
from optparse import OptionParser

def twice_nll(pars):
    return -2.0*model.logpdf(pars, data)[0]

def main(argv = None):
    
    if argv == None:
        argv = sys.argv[1:]
        
    usage = "usage: %prog [options]\n Run pyhf tests"
    
    parser = OptionParser(usage)
    parser.add_option("--npoints", default=10, type=int, help="Number of points to scan [default: %default]")
    parser.add_option("--min", default=0.5, type=float, help="Scan range min value [default: %default]")
    parser.add_option("--max", default=1.5, type=float, help="Scan range max value [default: %default]")
    parser.add_option("--combine", action="store_true", help="Run on combine inputs")
    
    (options, args) = parser.parse_args(sys.argv[1:])
    
    return options

if __name__ == '__main__':
    
    options = main()

    ws = os.environ['WS']
    wd = ws+'/validation'
    indir = wd+'/cards/combine/combine2pyhf' if options.combine else wd+'/cards/pyhf/combine2pyhf'
    logf = ws+'/logs/combine_fitpyhf.log' if options.combine else ws+'/logs/pyhf_fitpyhf.log'
    output = ws+'/results/combine' if options.combine else ws+'/results/pyhf'

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=logf,
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)
    
    logging.info('Start pyhf fits')
    pyhflog = logging.getLogger('fit.pyhf')
    
#    pyhf.set_backend('numpy', pyhf.optimize.minuit_optimizer(verbose=2))
    pyhf.set_backend('pytorch', pyhf.optimize.minuit_optimizer(verbose=2))
    
    dc = glob.glob(indir+'/*')
    
    for d in dc:
        dname = d.split('/')[-1]
        os.chdir(indir+'/'+dname)
        fc = glob.glob(indir+'/'+dname+'/*.json')
        for f in fc:
            fname = f.replace('.json', '')
            pyhflog.info('--> Run fits ('+dname+', '+fname.split('/')[-1]+')')
            pyhflog.info('--> Prepare the workspace')
            df = json.load(open(f))
            wspace = pyhf.Workspace(df)
            model = wspace.model(modifier_settings={'histosys': {'interpcode': 'code4p'}, 'normsys': {'interpcode': 'code4'}})
            
            init = model.config.suggested_init()
            constraints = model.config.suggested_bounds()
            names = model.config.par_names
            fixed = model.config.suggested_fixed()
            poi = names[model.config.poi_index]
            
            obs = wspace.data(model)
            asimov = model.expected_data(pyhf.tensorlib.astensor(init))
            fits = {'asi': asimov, 'obs': obs}

            for fit in fits.keys():
                data = asimov if fit == 'asi' else obs
                pyhflog.info('--> Perform the best fit ('+fit+')')
                start = timer()
                m = iminuit.Minuit(twice_nll, init, name=model.config.par_names)
                m.limits = constraints
                m.migrad()
                bf = m.values[model.config.poi_index]
                bfnll = m.fval
                end = timer()
                fittime = end-start
                pyhflog.info('    bf='+str(bf))
                inc = (options.max-options.min)/options.npoints
                muv = list(np.arange(options.min, options.max+inc, inc))
                utils.setprec(muv)
                if 1 not in muv: muv += utils.setprec([1])
                pyhflog.info('--> Perform the scan ('+fit+')')
                res = {'r': [], 'nll': []}
                res['bf'] = [bf]
                nllv = []
                for r in muv:
                    init[model.config.poi_index] = r
                    pfix = [(model.config.poi_index, r)]
                    for idx, fixed_val in pfix:
                        pname = model.config.par_names[idx]
                        m.values[pname] = fixed_val
                        m.fixed[pname] = True
                    m.migrad()
                    nllv.append(m.fval)
                for i in range(len(nllv)):
                    nllv[i] -= bfnll
                    res['r'].append(muv[i])
                    res['nll'].append(nllv[i])
                    pyhflog.info('    r='+str(muv[i])+', delta_nll='+str(nllv[i]))
                res['time'] = fittime
                utils.setprec(res['r'])
                utils.setprec(res['nll'], prec=6)
                utils.setprec(res['bf'], prec=6)
                fn = os.path.splitext(fname.split('/')[-1])[0]
                os.system('mkdir -p '+output+'/'+fn)
                json.dump(res, open(output+'/'+fn+'/'+fit+'_pyhf.json', 'w'), indent=2)