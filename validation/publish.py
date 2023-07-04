from optparse import OptionParser
import os, sys, glob
    
def main(argv = None):
    
    if argv == None:
        argv = sys.argv[1:]
        
    usage = "usage: %prog [options]\n Publish results"
        
    parser = OptionParser(usage)
    parser.add_option("--output", default='results', help="Output directory [default: %default]")
    
    (options, args) = parser.parse_args(sys.argv[1:])
    
    return options

if __name__ == '__main__':

    options = main()

    desc = {'stat': 'MC statistical uncertainties'}
    
    with open(options.output+'/README.md', 'w') as fr:
        intro = '# combine2pyhf\n\n An automated tool for a common validation of fit models using [combine](https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit) and [pyhf](https://github.com/scikit-hep/pyhf) packages.\n\n'
        fr.write(intro)
        for ct in ['stat']:
            dc = glob.glob(options.output+'/*'+ct+'*/')
            dc.sort(key=os.path.getmtime)
            fr.write('- '+desc[ct]+'\n\n')
            for d in dc:
                dname = d.split('/')[-2]
                fs = glob.glob(options.output+'/'+dname+'/nll_shape*.png')
                for f in fs:
                    fname = options.output.split('/')[-1]+'/'+dname+'/'+f.split('/')[-1]
                    mode = f.split('_')[-1].replace('.png', '')
                    title = dname+' ('+mode+')'
                    fr.write('  - <details>\n\n')
                    fr.write('    <summary>'+title+'</summary>\n\n')
                    fr.write('    !['+title+']('+fname.replace('nll_shape', 'time')+'?raw=true)\n\n')
                    fr.write('    !['+title+']('+fname+'?raw=true)\n\n')
                    fr.write('    !['+title+']('+fname.replace('_shape', '')+'?raw=true)\n\n')
                    fr.write('    </details>\n\n')
        fr.close()
                
