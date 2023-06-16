from optparse import OptionParser
import os, sys, math, glob, json, logging
import plotly
import plotly.graph_objects as go
import plotly.io as pio
pio.kaleido.scope.mathjax = None

def setprec(d):
    for k in d.keys():
        if k not in ['r']: prec = 1E+6
        else: prec = 1E+2
        d[k] = [math.ceil(v*prec)/prec for v in d[k]]
    
def main(argv = None):
    
    if argv == None:
        argv = sys.argv[1:]
        
    usage = "usage: %prog [options]\n Plot results"
        
    parser = OptionParser(usage)
    parser.add_option("--input", default='results', help="Input directory with results [default: %default]")
    
    (options, args) = parser.parse_args(sys.argv[1:])
    
    return options

if __name__ == '__main__':
    
    options = main()
    
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=os.environ['WS']+'/logs/plot.log',
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)
    
    logging.info('Start plotting')
    
    dc = glob.glob(options.input+'/*/')
    runs = []    
    for d in dc:
        card = d.split('/')[-2]
        fs = glob.glob(options.input+'/'+card+'/*combine*.json')
        for f in fs:
            proc = f.split('/')[-1]
            mode = proc[0]
                        
            combinedata = json.load(open(f, 'r'))
            setprec(combinedata)
            fpyhf = f.replace('_combine', '_pyhf')
            pyhfdata = json.load(open(fpyhf, 'r'))
            setprec(pyhfdata)
            
            data = [combinedata['nll'], pyhfdata['nll']]
            columns = ['r', 'deltaNLL (combine)', 'deltaNLL (pyhf)']
            
            analyticdata = None
            fanalytic = f.replace('_combine', '_analytic')
            if os.path.isfile(fanalytic):
                analyticdata = json.load(open(fanalytic, 'r'))
                columns.append('Analytic')
                data.append(analyticdata['nll'])
            if analyticdata: setprec(analyticdata)
            for rv in combinedata['r']:
                if (rv not in pyhfdata['r']) or (analyticdata and rv not in analyticdata['r']):
                    logging.error('The following signal strength value was not found in pyhf fits: '+str(rv))

            fig = go.Figure(data=[go.Table(
            header=dict(values=columns,
                        line_color='darkslategray',
                        fill_color='lightskyblue',
                        align='left'),
            cells=dict(values=combinedata['r']+data,
                       line_color='darkslategray',
                       fill_color='lightcyan',
                       height=20,
                       align='left'))
            ])

            fig.update_layout(height=23*(len(combinedata['r'])+1), margin=dict(l=10, r=10, t=10, b=10))
            fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
            fig.write_image(options.input+'/'+card+'/nll_'+mode+'.pdf')