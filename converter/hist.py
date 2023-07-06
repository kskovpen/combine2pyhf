#!/usr/bin/python3

import os, sys, math, glob, json
import numpy as np
from optparse import OptionParser
from collections import OrderedDict
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def main(argv = None):
    
    if argv == None:
        argv = sys.argv[1:]
                    
    usage = "usage: %prog [options]\n Plot json input data"
                        
    parser = OptionParser(usage)
    parser.add_option("--input", default='datacard.json', help="Input pyhf json file [default: %default]")
    parser.add_option("--output", default='datacard', help="Output figure name [default: %default]")
    
    (options, args) = parser.parse_args(sys.argv[1:])
    
    return options

if __name__ == '__main__':
                                    
    options = main()
    
    data, pred, uncorrup, uncorrdown = OrderedDict(), OrderedDict(), OrderedDict(), OrderedDict()
    colors = [plt.cm.Pastel1(i) for i in range(100)]

    res = json.load(open(options.input))
    chs = res['channels']
    obs = res['observations']
    obsdata, obsdataerr, obsbins = [], [], []
    procs = []
    ibin = 0
    for ich, ch in enumerate(chs):
        obsd = obs[ich]['data']
        samps = ch['samples']
        for samp in samps:
            proc = samp['name']
            mods = samp['modifiers']
            if proc not in procs: procs.append(proc)
            d = samp['data']
            nbins = len(d)
            for ib in range(nbins):
                ibin = nbins*ich+ib
                if ibin not in data.keys(): data[ibin] = {}
                data[ibin][proc] = d[ib]
                for m in mods:
                    if ibin not in uncorrup.keys(): uncorrup[ibin] = 0
                    if m['type'] in ['staterror']:
                        uncorrup[ibin] += m['data'][ib]**2
                    if ibin not in uncorrdown.keys(): uncorrdown[ibin] = 0
                    if m['type'] in ['staterror']:
                        uncorrdown[ibin] += m['data'][ib]**2
                if ibin not in pred.keys(): pred[ibin] = 0
                pred[ibin] += d[ib]
        for ib in range(nbins):
            ibin = nbins*ich+ib
            obsbins.append(ibin+0.5)
            obsdata.append(obsd[ib])
            obsdataerr.append(math.sqrt(obsdata[-1]))
    for ib in uncorrup.keys():
        uncorrup[ib] = math.sqrt(uncorrup[ib])
    for ib in uncorrdown.keys():
        uncorrdown[ib] = math.sqrt(uncorrdown[ib])

    ymax = 0
    for ib in data.keys():
        ym = sum([data[ib][p] for p in data[ib].keys()])
        ymdata = max(obsdata)        
        if ym > ymax: ymax = ym
        if ymdata > ymax: ymax = ymdata
                
    fig, ax = plt.subplots()
    plbins, pldata, plcol = [], [], []
    for ip, p in enumerate(procs):
        dp, dbins = [], []
        for ib in data.keys():
            dbins.append(int(ib))
            dp.append(data[ib][p])        
        dbins.append(dbins[-1]+1.0)
        dp.append(0)
        plbins.append(dbins)
        pldata.append(dp)
        plcol.append(colors[ip])
    
    ax.hist(plbins, len(plbins)+1, weights=pldata, stacked=True, label=procs, color=plcol)
    ax.errorbar(obsbins, obsdata, yerr=obsdataerr, fmt='.', color='black', lw=2, alpha=1.0, label='data')
    yerrup = [v for k, v in uncorrup.items()]
    yerrdown = [v for k, v in uncorrdown.items()]
    ypred = [v for k, v in pred.items()]
    for iy, y in enumerate(ypred):
        ax.add_patch(patches.Rectangle((obsbins[iy]-0.5, ypred[iy]+(yerrup[iy]-yerrdown[iy])/2.0-(yerrup[iy]+yerrdown[iy])/2.0), 1.0, yerrup[iy]+yerrdown[iy], alpha=0.1, fc='black', hatch='/', edgecolor='black', linewidth=0.0))
    ax.set_title('Input data')
    ax.set_xlabel('Bins')
    ax.set_ylabel('Events')
    ax.set_ylim([0.0, 1.2*ymax])
    ax.set_xticks(np.arange(0.5, len(plbins)+1.5, 1.0))
    xlabels = [str(int(float(item.get_text())-0.5)) for item in ax.get_xticklabels()]
    ax.set_xticklabels(xlabels)
    handles, labels = plt.gca().get_legend_handles_labels()    
    order = [len(labels)-1]
    for v in range(len(labels)):
        if v in order: continue
        else: order.append(v)
    plt.legend([handles[idx] for idx in order],[labels[idx] for idx in order], loc="best", fancybox=True, framealpha=0.1)
    fig.savefig(options.output+'.png', dpi=300)