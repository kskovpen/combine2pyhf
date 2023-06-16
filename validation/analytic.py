import os, sys, math, json, glob, logging, subprocess
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

    ws = os.environ['WS']
    wd = ws+'/validation'
    indir = wd+'/cards/pyhf/combine2pyhf'

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=ws+'/logs/analytic.log',
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)
    
    logging.info('Start analytic calculations')
    log = logging.getLogger('fit.analytic')
    
    fits = ['asi', 'obs']
    
    dc = glob.glob(indir+'/*')        

    for d in dc:
        dname = d.split('/')[-1]
        if dname == 'one-bin':
            fc = glob.glob(indir+'/'+dname+'/*.json')
            for f in fc:
                fname = os.path.splitext(f.split('/')[-1])[0]
                if fname == 'one-bin-stat-bbl':
                    
                    log.info('--> Calculate ('+dname+', '+fname+')')
                    
                    df = json.load(open(f))
                    sig = df['channels'][0]['samples'][0]['data'][0]
                    sigErr = df['channels'][0]['samples'][0]['modifiers'][1]['data'][0]
                    bkg = df['channels'][0]['samples'][1]['data'][0]
                    bkgErr = df['channels'][0]['samples'][1]['modifiers'][0]['data'][0]
                    data = df['observations'][0]['data'][0]
                    
                    muv = [0.5, 0.7, 0.9, 1.1, 1.3, 1.5]
                    
                    for fit in fits:
                        log.info('--> Perform the scan ('+fit+')')
                        n = sig+bkg if fit == 'asi' else data
                        nllv = []
                        for mu in muv:
                            pred = sig*mu+bkg
                            err = math.sqrt((sigErr*mu)**2+(bkgErr)**2)/pred
                            a = 1
                            b = pred*err*err-1
                            c = -n*err*err
                            sqr = math.sqrt(b*b-4*a*c)
                            x1 = (-b+sqr)/2/a
                            x2 = (-b-sqr)/2/a
                            nll = -n*math.log(x1*pred)+x1*pred+(x1-1)**2/2/(err)**2
                            nllv.append(nll)
                                
                        bf = muv[nllv.index(min(nllv))]
                        bfnll = min(nllv)
                        log.info('    bf='+str(bf))
    
                        res = {'r': [], 'nll': []}
                        for i in range(len(nllv)):
                            nllv[i] -= bfnll
                            nllv[i] *= 2.0
                            res['r'].append(muv[i])
                            res['nll'].append(nllv[i])
                            log.info('    r='+str(muv[i])+', delta_nll='+str(nllv[i]))
                        fn = os.path.splitext(fname.split('/')[-1])[0]
                        os.system('mkdir -p '+ws+'/results/'+fn)
                        json.dump(res, open(ws+'/results/'+fn+'/'+fit+'_analytic.json', 'w'), indent=2)