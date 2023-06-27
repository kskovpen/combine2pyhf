import os, sys, math, json, glob, logging, subprocess, pyhf, iminuit
import numpy as np
from optparse import OptionParser

def twice_nll(pars):
    return -2.0*model.logpdf(pars, data)[0]

def execute(logger, c):
    try:
        r = subprocess.check_output(c, stderr=subprocess.STDOUT, shell=True)
        logger.debug(r)
    except subprocess.CalledProcessError as e:
        logger.error(e.output)

def main(argv = None):
    
    if argv == None:
        argv = sys.argv[1:]
        
    usage = "usage: %prog [options]\n Run pyhf tests"
    
    parser = OptionParser(usage)
    parser.add_option("--npoints", default=20, type=int, help="Number of points to scan [default: %default]")
    parser.add_option("--min", default=0.5, type=float, help="Scan range min value [default: %default]")
    parser.add_option("--max", default=1.5, type=float, help="Scan range max value [default: %default]")
    
    (options, args) = parser.parse_args(sys.argv[1:])
    
    return options

if __name__ == '__main__':
    
    options = main()

    ws = os.environ['WS']
    wd = ws+'/validation'
    indir = wd+'/cards/pyhf/combine2pyhf'

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
    
    pyhf.set_backend('numpy', pyhf.optimize.minuit_optimizer(verbose=2))    
    
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
                m = iminuit.Minuit(twice_nll, init, name=model.config.par_names)
                m.limits = constraints
                m.migrad()
                bf = m.values[model.config.poi_index]
                pyhflog.info('    bf='+str(bf))
                muv = [1.0]+list(np.arange(options.min, options.max, (options.max-options.min)/options.npoints))
                pyhflog.info('--> Perform the scan ('+fit+')')
                res = {'r': [], 'nll': []}
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
                bf = muv[nllv.index(min(nllv))]
                bfnll = min(nllv)
                for i in range(len(nllv)):
                    nllv[i] -= bfnll
                    res['r'].append(muv[i])
                    res['nll'].append(nllv[i])
                    pyhflog.info('    r='+str(muv[i])+', delta_nll='+str(nllv[i]))
                fn = os.path.splitext(fname.split('/')[-1])[0]
                os.system('mkdir -p '+ws+'/results/'+fn)
                json.dump(res, open(ws+'/results/'+fn+'/'+fit+'_pyhf.json', 'w'), indent=2)