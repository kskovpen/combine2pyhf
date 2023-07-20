from optparse import OptionParser
import os, sys, math, glob, json, logging
import utils
import plotly
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
piodef = pio.kaleido.scope.mathjax
    
def main(argv = None):
    
    if argv == None:
        argv = sys.argv[1:]
        
    usage = "usage: %prog [options]\n Plot results"
        
    parser = OptionParser(usage)
    parser.add_option("--input", default='results', help="Input directory with results [default: %default]")
    parser.add_option("--combine", action="store_true", help="Run on combine inputs")
    
    (options, args) = parser.parse_args(sys.argv[1:])
    
    return options

if __name__ == '__main__':
    
    options = main()

    logf = os.environ['WS']+'/logs/plot_combine.log' if options.combine else os.environ['WS']+'/logs/plot_pyhf.log'
    
    color = {'combine': '#f55a42', 'pyhf': '#4343d9', 'analytic': '#48ab37'}
    
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
    
    logging.info('Plot '+('results for combine inputs' if options.combine else 'results for pyhf inputs')+' ..')
    
    layout = go.Layout(
      paper_bgcolor='rgba(0,0,0,0)',
      plot_bgcolor='rgba(0,0,0,0)'
    )
    
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
            
            data = [combined['nll'], pyhfd['nll']]
            columns = ['r', 'deltaNLL (combine)', 'deltaNLL (pyhf)']
            
            analyticdata = None
            fanalytic = f.replace('combine', 'analytic')
            print(fanalytic)
            analyticd = {}
            if os.path.isfile(fanalytic):
                logging.info('Found analytic results')
                analyticdata = json.load(open(fanalytic, 'r'))
                columns.append('Analytic')
                data.append(analyticdata['nll'])
                analyticd['r'] = sorted(analyticdata['r'])
                analyticd['nll'] = [x for _, x in sorted(zip(analyticd['r'], analyticdata['nll']))]
            for rv in combined['r']:
                if (rv not in pyhfd['r']) or (analyticdata and rv not in analyticd['r']):
                    logging.error('The following signal strength value was not found in pyhf fits: '+str(rv))

            rows = [combined['r'], data[0], data[1]]
            if analyticdata: rows = [combined['r'], data[0], data[1], data[2]]
                    
            fig = go.Figure(data=[go.Table(
            header=dict(values=['model', 'time (combine) [s]', 'time (pyhf) [s]'],
                        line_color='darkslategray',
                        fill_color='lightskyblue',
                        align='left'),
            cells=dict(values=[[card], combinedata['time'], pyhfdata['time']],
                       line_color='darkslategray',
                       fill_color='lightcyan',
                       height=20,
                       align='left'))
            ], layout=layout)

            pio.kaleido.scope.mathjax = None
            fig.update_layout(height=70, margin=dict(l=10, r=10, t=10, b=10))
            fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
            fig.write_image(options.input+'/'+card+'/time_'+mode+'.png', scale=2)

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
            ], layout=layout)

            pio.kaleido.scope.mathjax = None
            fig.update_layout(height=21*(len(combined['r'])+1), margin=dict(l=10, r=10, t=10, b=10))
            fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))
            fig.write_image(options.input+'/'+card+'/nll_'+mode+'.png', scale=2)
            
            pio.kaleido.scope.mathjax = piodef
            combd = go.Scatter(x=combined['r'], y=combined['nll'], name='combine', line=dict(color=color['combine']))
            pyhfd = go.Scatter(x=pyhfd['r'], y=pyhfd['nll'], name='pyhf', line=dict(color=color['pyhf']))
            if analyticdata: analyticd = go.Scatter(x=analyticd['r'], y=analyticd['nll'], name='analytic', line=dict(color=color['analytic'], dash='dot'))
            fignll = make_subplots(specs=[[{"secondary_y": False}]])
            fignll.add_trace(combd)
            fignll.add_trace(pyhfd, secondary_y=False)
            if analyticdata: fignll.add_trace(analyticd, secondary_y=False)
            ymax = max(combined['nll'])
            fignll.add_annotation(x=1.0, y=ymax-ymax/10, text=r'$\hat{\mu}\text{ = '+str(combinedata['bf'][0])+'}$', font=dict(family="sans serif", size=16, color=color['combine']))
            fignll.add_annotation(x=1.0, y=ymax-2.*ymax/10, text=r'$\hat{\mu}\text{ = '+str(pyhfdata['bf'][0])+'}$', font=dict(family="sans serif", size=16, color=color['pyhf']))
            if analyticdata: fignll.add_annotation(x=1.0, y=ymax-3.*ymax/10, text=r'$\hat{\mu}\text{ = '+str(analyticdata['bf'][0])+'}$', font=dict(family="sans serif", size=16, color=color['analytic']))
            fignll.update_annotations(showarrow=False)
            fignll.update_layout(xaxis_title='r', yaxis_title=r'$\text{-2 }\Delta\text{ ln L}$', margin=dict(l=5, r=5, t=5, b=5))
            fignll.write_image(options.input+'/'+card+'/nll_shape_'+mode+'.png', scale=2)