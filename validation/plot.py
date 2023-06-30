from optparse import OptionParser
import os, sys, math, glob, json, logging
import plotly
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
piodef = pio.kaleido.scope.mathjax

def setprec(d):
    for k in d.keys():
        if k not in ['r']: prec = 1E+6
        else: prec = 1E+2
        d[k] = [round(v*prec)/prec for v in d[k]]
    
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
            mode = f.split('/')[-1].split('_')[0]
            fpyhf = f.replace('_combine', '_pyhf')
            
            combined = {}
            combinedata = json.load(open(f, 'r'))
            combined['r'] = sorted(combinedata['r'])
            combined['nll'] = [x for _, x in sorted(zip(combinedata['r'], combinedata['nll']))]

            pyhfd = {}
            pyhfdata = json.load(open(fpyhf, 'r'))
            pyhfd['r'] = sorted(pyhfdata['r'])
            pyhfd['nll'] = [x for _, x in sorted(zip(pyhfdata['r'], pyhfdata['nll']))]
                        
            setprec(combined)
            setprec(pyhfd)
            
            data = [combined['nll'], pyhfd['nll']]
            columns = ['r', 'deltaNLL (combine)', 'deltaNLL (pyhf)']
            
            analyticdata = None
            fanalytic = f.replace('_combine', '_analytic')
            analyticd = {}
            if os.path.isfile(fanalytic):
                analyticdata = json.load(open(fanalytic, 'r'))
                columns.append('Analytic')
                data.append(analyticdata['nll'])
                analyticd['r'] = sorted(analyticdata['r'])
                analyticd['nll'] = [x for _, x in sorted(zip(analyticdata['r'], analyticdata['nll']))]
            if analyticdata: setprec(analyticd)
            for rv in combined['r']:
                if (rv not in pyhfd['r']) or (analyticdata and rv not in analyticd['r']):
                    logging.error('The following signal strength value was not found in pyhf fits: '+str(rv))

            rows = [combined['r'], data[0], data[1]]
            if analyticdata: rows = [combined['r'], data[0], data[1], data[2]]
                    
            fig = go.Figure(data=[go.Table(
            header=dict(values=columns,
                        line_color='darkslategray',
                        fill_color='lightskyblue',
                        align='left'),            
            cells=dict(values=rows,
                       line_color='darkslategray',
                       fill_color='lightcyan',
                       height=20,
                       align='left'))
            ])

            pio.kaleido.scope.mathjax = None
            fig.update_layout(height=23*(len(combined['r'])+1), margin=dict(l=10, r=10, t=10, b=10))
            fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
            fig.write_image(options.input+'/'+card+'/nll_'+mode+'.png', scale=2)
            
            pio.kaleido.scope.mathjax = piodef
            combd = go.Scatter(x=combined['r'], y=combined['nll'], name='combine')
            pyhfd = go.Scatter(x=pyhfd['r'], y=pyhfd['nll'], name='pyhf')
            fignll = make_subplots(specs=[[{"secondary_y": True}]])
            fignll.add_trace(combd)
            fignll.add_trace(pyhfd, secondary_y=True)
            fignll.update_layout(xaxis_title='Signal strength', yaxis_title=r'$-2\Delta\text{ ln N}$', margin=dict(l=5, r=5, t=5, b=5))
            fignll.write_image(options.input+'/'+card+'/nll_shape_'+mode+'.png', scale=2)
            
            