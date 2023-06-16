from optparse import OptionParser
import os, sys, glob, json, logging
from decimal import *
import plotly
import plotly.graph_objects as go
import plotly.io as pio
print(plotly.__version__)
print(pio.kaleido.__version__)
pio.kaleido.scope.mathjax = None

def setprec(data):
    for k in data.keys: data[k] = [+Decimal(v) for v in data[k]]
    
def main(argv = None):
    
    if argv == None:
        argv = sys.argv[1:]
        
    usage = "usage: %prog [options]\n Plot results"
        
    parser = OptionParser(usage)
    parser.add_option("--input", default='results', help="Input directory with results [default: %default]")
    
    (options, args) = parser.parse_args(sys.argv[1:])
    
    return options

if __name__ == '__main__':

    getcontext().prec = 6
    
    options = main()
    
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=ws+'/logs/plot.log',
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
        card = d.split('_')[-1]
        fs = glob.glob(options.input+'/'+card+'/*combine*.json')
        for f in fs:
            proc = f.split('/')[-1]
            mode = proc[0]
                        
            combinedata = json.load(open(f, 'r'))
            setprec(combinedata)
            fpyhf = f.replace('combine', 'pyhf')
            pyhfdata = json.load(open(fpyhf, 'r'))
            
            data = [combinedata['nll'], pyhfdata['nll']]
            columns = ['r', 'deltaNLL (combine)', 'deltaNLL (pyhf)']
            
            analyticdata = f.replace('combine', 'analytic')            
            if os.path.isfile(f.replace('combine', 'analytic')):
                analyticdata = json.load(open(analyticdata, 'r'))
                columns.append('Analytic')
                data.append(analyticdata['nll'])
            for rv in combinedata['r']:
                if (rv not in pyhfdata['r']) or (analyticdata and rv not in analyticdata['r']):
                    logging.error('The following signal strength value was not found in pyhf fits:', rv)

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