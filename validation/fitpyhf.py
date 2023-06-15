import os, sys, math, json, glob, logging, subprocess, pyhf, iminuit
from optparse import OptionParser

def twice_nll(pars):
    return -2.0*model.logpdf(pars, data)[0]

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
            
            m = iminuit.Minuit(twice_nll, init, name=model.config.par_names)
            m.limits = constraints
            for fit in fits.keys():
                data = asimov if fit == 'asi' else obs
                pyhflog.info('--> Perform the best fit ('+fit+')')
                m.migrad()
                bf = m.values[model.config.poi_index]
                pyhflog.info('    bf='+str(bf))
                muv = [0.68, 0.84, 1, 1.16, 1.32]
                pyhflog.info('--> Perform the scan ('+fit+')')
                nllv = []
                for r in muv:
                    init[model.config.poi_index] = r
                    constraints = [(model.config.poi_index, r)]
                    for idx, fixed_val in constraints:
                        pname = model.config.par_names[idx]
                        m.values[pname] = fixed_val
                        m.fixed[pname] = True
                    m.migrad()
                    nllv.append(m.fval)
                bf = muv[nllv.index(min(nllv))]
                bfnll = min(nllv)
                for i in range(len(nllv)):
                    nllv[i] -= bfnll
                    pyhflog.info('    r='+str(muv[i])+', delta_nll='+str(nllv[i]))                