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

    with open(options.output+'/README.md', 'w') as fr:
        intro = '# combine2pyhf\n\n An automated tool for common validation of fit models in combine and pyhf tools.\n'
        fr.write(intro)
        dc = glob.glob('results/*/')
        for d in dc:
            fs = glob.glob('results/'+d+'/nll*.pdf')
            for f in fs:
                mode = f.split('_')[-1].replace('.pdf', '')
                title = d+' ('+mode+')'
                fr.write('**'+title+'**\n')
                fr.write('!['+title+']('+f+'?raw=true\n')
        fr.close()
                
