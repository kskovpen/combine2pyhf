#!/usr/bin/python3

import os, sys, math, glob, json
import numpy as np
from optparse import OptionParser
from collections import OrderedDict
import matplotlib as mpl
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
    
    os.system('rm -rf '+mpl.get_cachedir()+'/font*')
    
    data, pred, uncorrup, uncorrdown, corrup, corrdown = (OrderedDict() for _ in range(6))
    colors = [plt.cm.Pastel1(i) for i in range(100)]

    res = json.load(open(options.input))
    chs = res['channels']
    obs = res['observations']
    
    nuis = []
    for ch in chs:
        nuis.append({})
        for isamp, s in enumerate(ch['samples']):
            for m in s['modifiers']:
                if 'r_' not in m['name'] and 'prop' not in m['name']:
                    if m['name'] not in nuis[-1].keys(): nuis[-1][m['name']] = [ch['samples'][isamp]['name']]
                    else: nuis[-1][m['name']].append(ch['samples'][isamp]['name'])
    
    obsdata, obsdataerr, obsbins = [], [], []
    dnup, dndown = [], []
    corrup, corrdown = [], []
    procs = []
    ibin = 0
    ntotbin = 0
    for ich, ch in enumerate(chs):
        obsd = obs[ich]['data']
        samps = ch['samples']
        
        nbins = len(samps[0]['data'])
        
        corrup.append(OrderedDict())
        corrdown.append(OrderedDict())
        
        for m in nuis[ich].keys():
            if len(nuis[ich][m]) > 1:                
                if m not in corrup[ich].keys():
                    corrup[ich][m] = {}
                    corrdown[ich][m] = {}
                    for ib in range(nbins):
                        ibin = ntotbin+ib
                        corrup[ich][m][ibin] = 0
                        corrdown[ich][m][ibin] = 0
                        for s in nuis[ich][m]:
                            for samp in samps:
                                if samp['name'] == s:
                                    for ist, st in enumerate(samp['modifiers']):
                                        if st['name'] == m:
                                            if st['type'] in ['histosys']:
                                                corrup[ich][m][ibin] += samp['modifiers'][ist]['data']['hi_data'][ib]-samp['data'][ib]
                                                corrdown[ich][m][ibin] += samp['modifiers'][ist]['data']['lo_data'][ib]-samp['data'][ib]
                                            elif st['type'] in ['normsys']:
                                                corrup[ich][m][ibin] += samp['data'][ib]*abs(samp['modifiers'][ist]['data']['hi']-1.0)
                                                corrdown[ich][m][ibin] += samp['data'][ib]*abs(samp['modifiers'][ist]['data']['lo']-1.0)

        for samp in samps:
            proc = samp['name']
            mods = samp['modifiers']
            if proc not in procs: procs.append(proc)
            d = samp['data']
#            nbins = len(d)
            
            for ib in range(nbins):
                ibin = ntotbin+ib
                if ibin not in data.keys(): data[ibin] = {}
                data[ibin][proc] = d[ib]
                for m in mods:
                    
                    if ibin not in uncorrup.keys(): uncorrup[ibin] = 0
                    if 'prop' in m['name']:
                        uncorrup[ibin] += m['data'][ib]**2
                    if m['name'] in nuis[ich].keys() and len(nuis[ich][m['name']]) < 2:
                        if m['type'] in ['histosys']:
                            uncorrup[ibin] += (m['data']['hi_data'][ib]-d[ib])**2
                        elif m['type'] in ['normsys']:
                            uncorrup[ibin] += ((m['data']['hi']-1.0)*d[ib])**2
                        
                    if ibin not in uncorrdown.keys(): uncorrdown[ibin] = 0
                    if 'prop' in m['name']:
                        uncorrdown[ibin] += m['data'][ib]**2
                    if m['name'] in nuis[ich].keys() and len(nuis[ich][m['name']]) < 2:
                        if m['type'] in ['histosys']:
                            uncorrdown[ibin] += (m['data']['lo_data'][ib]-d[ib])**2
                        elif m['type'] in ['normsys']:
                            uncorrdown[ibin] += ((m['data']['lo']-1.0)*d[ib])**2
                        
                if ibin not in pred.keys(): pred[ibin] = 0
                pred[ibin] += d[ib]
        for ib in range(nbins):
            ibin = nbins*ich+ib
            obsbins.append(ibin+0.5)
            obsdata.append(obsd[ib])
            obsdataerr.append(math.sqrt(obsdata[-1]))
            
        ntotbin += nbins
            
    ntotbin = 0
    for ich, ch in enumerate(chs):
        samps = ch['samples']
        nbins = len(samps[0]['data'])
        for im, m in enumerate(corrup[ich].keys()):
            for ib in range(nbins):
                ibin = ntotbin+ib
                if im == 0: 
                    dnup.append(corrup[ich][m][ibin]**2)
                    dndown.append(corrdown[ich][m][ibin]**2)
                else:
                    dnup[ibin] += corrup[ich][m][ibin]**2
                    dndown[ibin] += corrdown[ich][m][ibin]**2
        ntotbin += nbins
    for ib in range(len(dnup)):
        dnup[ib] = math.sqrt(dnup[ib])
        dndown[ib] = math.sqrt(dndown[ib])

    totalup, totaldown = [], []
    for ib in range(len(uncorrup.keys())):
        totalup.append(0)
        totaldown.append(0)
    if len(totalup) == 0:
        for ib in range(len(dnup)):
            totalup.append(0)
            totaldown.append(0)
    
    for ib in uncorrup.keys():
        uncorrup[ib] = math.sqrt(uncorrup[ib])
        totalup[ib] += uncorrup[ib]
    for ib in uncorrdown.keys():
        uncorrdown[ib] = math.sqrt(uncorrdown[ib])
        totaldown[ib] += uncorrdown[ib]

    for ib in range(len(dnup)):
        totalup[ib] = math.sqrt(totalup[ib]**2+dnup[ib]**2)
        totaldown[ib] = math.sqrt(totaldown[ib]**2+dndown[ib]**2)

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
            if p not in data[ib].keys(): continue
            dbins.append(int(ib))
            dp.append(data[ib][p])
        dbins.append(dbins[-1]+1.0)
        dp.append(0)
        plbins.append(dbins)
        pldata.append(dp)
        plcol.append(colors[ip])
    
    ax.hist(plbins, len(obsdata), weights=pldata, stacked=True, label=procs, color=plcol)
    ax.errorbar(obsbins, obsdata, yerr=obsdataerr, fmt='.', color='black', lw=2, alpha=1.0, label='data')
    yerrup = totalup
    yerrdown = totaldown
    ypred = [v for k, v in pred.items()]
    for iy, y in enumerate(ypred):
        ax.add_patch(patches.Rectangle((obsbins[iy]-0.5, ypred[iy]+(yerrup[iy]-yerrdown[iy])/2.0-(yerrup[iy]+yerrdown[iy])/2.0), 1.0, yerrup[iy]+yerrdown[iy], alpha=0.1, fc='black', hatch='/', edgecolor='black', linewidth=0.0))
    ax.set_title('Input data')
    ax.set_xlabel('Bins')
    ax.set_ylabel('Events')
    ax.set_ylim([0.0, 1.2*ymax])
    ax.set_xticks(np.arange(0.5, len(obsbins)+0.5, 1.0))
    plt.draw()
    xlabels = [str(int(float(item.get_text())-0.5)) for item in ax.get_xticklabels()]
    ax.set_xticklabels(xlabels)
    handles, labels = plt.gca().get_legend_handles_labels()    
    order = [len(labels)-1]
    for v in range(len(labels)):
        if v in order: continue
        else: order.append(v)
    plt.legend([handles[idx] for idx in order],[labels[idx] for idx in order], loc="best", fancybox=True, framealpha=0.1)
    fig.savefig(options.output+'.png', dpi=300)