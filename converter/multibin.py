#!/usr/bin/python3

import os, sys, glob, ROOT, subprocess, json, copy
from optparse import OptionParser

ws = os.environ['WS']
wd = ws+'/validation'

sys.path.append(wd)
import utils

def main(argv = None):
    
    if argv == None:
        argv = sys.argv[1:]
        
    usage = "usage: %prog [options]\n Clone bins"
    
    parser = OptionParser(usage)
    parser.add_option("--nbins", default=9, type=int, help="The number of additional bins to create [default: %default]")
    
    (options, args) = parser.parse_args(sys.argv[1:])
    
    return options

if __name__ == '__main__':
    
    options = main()

    os.system('mkdir -p '+ws+'/cards/combine/multi-bin')
    os.system('mkdir -p '+ws+'/cards/pyhf/multi-bin')

    # combine cards
    ro = glob.glob(ws+'/cards/combine/one-bin/*.root')
    for r in ro:
        os.system('cp '+r+' '+ws+'/cards/combine/multi-bin/'+r.split('/')[-1].replace('one-bin', 'multi-bin'))
    dc = glob.glob(ws+'/cards/combine/one-bin/*.txt')
    for d in dc:
        with open(d, 'r') as fr:
            lines = fr.readlines()
            for il, l in enumerate(lines):
                if 'imax 1 number of bins' in l:
                    lines[il] = 'imax '+str(options.nbins+1)+' number of bins\n'
                elif 'shapes' in l:
                    lines[il] = l.replace('one-bin', 'multi-bin')+'\n'
                    for i in range(options.nbins): lines[il] += l.replace('ch1 ', 'ch'+str(i+2)+' ').replace('ch1/', 'ch'+str(i+2)+'/').replace('one-bin', 'multi-bin')+'\n'
                elif 'bin          ch1\n' == l:
                    lines[il] = 'bin          ch1 '
                    for i in range(options.nbins): lines[il] += 'ch'+str(i+2)+' '
                    lines[il] += '\n'
                elif 'observation  -1' in l:
                    lines[il] = 'observation  -1 '
                    for i in range(options.nbins): lines[il] += '-1 '
                    lines[il] += '\n'
                elif 'bin          ch1 ch1\n' == l:
                    lines[il] = 'bin          ch1 ch1 '
                    for i in range(options.nbins): lines[il] += 'ch'+str(i+2)+' ch'+str(i+2)+' '
                    lines[il] += '\n'
                elif 'process      sig bkg\n' == l:
                    lines[il] = 'process      sig bkg '
                    for i in range(options.nbins): lines[il] += 'sig bkg '
                    lines[il] += '\n'
                elif 'process      0 1\n' == l:
                    lines[il] = 'process      0 1 '
                    for i in range(options.nbins): lines[il] += '0 1 '
                    lines[il] += '\n'
                elif 'rate         -1 -1\n' == l:
                    lines[il] = 'rate         -1 -1 '
                    for i in range(options.nbins): lines[il] += '-1 -1 '
                    lines[il] += '\n'
                elif 'lnN' in l or ('shape' in l and not 'shapes' in l):
                    ld = l.split()
                    lines[il] = l[:-2]
                    for i in range(options.nbins): lines[il] += ' '+ld[-2]+' '+ld[-1]+' '
                    lines[il] += '\n'
                elif 'autoMCStats' in l:
                    lines[il] += '\n'
                    for i in range(options.nbins): lines[il] += l.replace('ch1 ', 'ch'+str(i+2)+' ')+'\n'
            with open(d.replace('one-bin', 'multi-bin'), 'w') as fw:
                for l in lines:
                    fw.write(l)
#            with open(d.replace('one-bin', 'multi-bin'), 'r') as ff:
#                lines = ff.readlines()
#                for l in lines:
#                    print(l)

    dc = glob.glob(ws+'/cards/combine/multi-bin/*.root')
    for d in dc:
        f = ROOT.TFile(d, 'UPDATE')
        for i in range(options.nbins):
            f.WriteObject(f.GetDirectory('ch1'), 'ch'+str(i+2))
        f.Write()
        f.Close()

    # pyhf cards
    dc = glob.glob(ws+'/cards/pyhf/one-bin/*.json')
    for d in dc:
        res = json.load(open(d))
        for i in range(options.nbins):
            res['channels'] += [copy.deepcopy(res['channels'][0])]
            res['channels'][-1]['name'] = 'ch'+str(i+2)
            res['observations'] += [copy.deepcopy(res['observations'][0])]
            res['observations'][-1]['name'] = 'ch'+str(i+2)
        for ch in res['channels']:
            samp = ch['samples']
            for isamp, s in enumerate(samp):
                mod = samp[isamp]['modifiers']
                for im, m in enumerate(mod):
                    if m['name'] != 'r_sig':
                        mod[im]['name'] = m['name'].replace('ch1', ch['name'])
        json.dump(res, open(d.replace('one-bin', 'multi-bin'), 'w'), indent=2)
#        with open(d.replace('one-bin', 'multi-bin'), 'r') as ff:
#            lines = ff.readlines()
#            for l in lines:
#                print(l)