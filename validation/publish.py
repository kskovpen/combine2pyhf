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
        intro = '# combine2pyhf\n\n An automated tool for common validation of fit models in combine and pyhf packages.\n\n'
        fr.write(intro)
        dc = glob.glob(options.output+'/*/')
        for d in dc:
            dname = d.split('/')[-2]
            fs = glob.glob(options.output+'/'+dname+'/nll*.pdf')
            for f in fs:
                fname = options.output+'/'+dname+'/'+f.split('/')[-1]
                mode = f.split('_')[-1].replace('.pdf', '')
                title = dname+' ('+mode+')'
                fr.write('**'+title+'**\n\n')
                fr.write('!['+title+']('+fname+'?raw=true)\n\n')
        fr.close()
                
