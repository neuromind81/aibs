# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 15:07:31 2013

@author: saskiad
"""

def plotonecell(oridata, sfdata, tfdata, sftfdata, rfdata, cellnumber, ori):
    '''script to plot all the data for one cell'''
    oriF1m = loadh5(oridata, 'f1mean')
    oriF1s = loadh5(oridata, 'f1sem')
    
    sfF1m = loadh5(sfdata, 'f1mean')
    sfF1s = loadh5(sfdata, 'f1sem')
    
    tfF1m = loadh5(tfdata, 'f1mean')
    tfF1s = loadh5(tfdata, 'f1sem')

    stF1m = loadh5(sftfdata, 'f1mean')

    onrf = loadh5(rfdata, 'onrf')
    offrf = loadh5(rfdata, 'offrf')

    figure()
    ax1 = subplot(3,2,1)
    ax1.errorbar(tuning, oriF1m[:,cellnumber], yerr=oriF1sm[:,cellnumber], fmt = 'ko', capsize=2, linestyle='-')
    ax1.set_ylabel('F1', fontsize=10)
    ax1.set_ylim(bottom=0)
    xticks(range(0,361,90))             
    xlabel('Orientation (Deg)', fontsize=10)
    tick_params(axis='both', which='major', labelsize=7)
    
    subplot(3,2,2)
    imshow(stF1m[:,:,cellnumber:(ori/120)], origin='lower',cmap='gray')
    xticks(range(3), ['1', '4', '15'])
    yticks(range(3), ['0.05','0.1','0.2'])
    xlabel('TF (Cyc/Sec)', fontsize=10)
    ylabel('SF (Cyc/Deg)', fontsize=10)
    tick_params(axis='both', which='major', labelsize=7)             
    cbar = colorbar()
    cbar.ax.set_ylabel('F1', fontsize=8)
    for t in cbar.ax.get_yticklabels():
        t.set_fontsize(8)
    
    ax2 = subplot(3,2,3)
    ax2.set_xscale("log", nonposx='clip')    
    ax2.errorbar(tuning, sfF1m[:,cellnumber,(ori/120)], yerr=sfF1s[:,cellnumber,(ori/120)], fmt = 'ko', capsize=2, linestyle='-') 
    ax2.set_ylabel('F1', fontsize=10)
    ax2.set_ylim(bottom=0)
    xticks(np.arange(0, 0.62, 0.1))             
    xlabel('Spatial Frequency (Cyc/Deg)', fontsize=10)
    tick_params(axis='both', which='major', labelsize=7)
    
    ax3 = subplot(3,2,4)
    ax3.set_xscale("log", nonposx='clip')    
    ax3.errorbar(tuning, tfF1m[:,cellnumber,(ori/120)], yerr=tfF1s[:,cellnumber,(ori/120)], fmt = 'ko', capsize=2, linestyle='-')
    ax3.set_ylabel('F1', fontsize=10)
    ax3.set_ylim(bottom=0)
    xticks(range(0,15,3))             
    xlabel('Temporal Frequency (Cyc/Sec)', fontsize=10)
    tick_params(axis='both', which='major', labelsize=7)
    
    subplot(3,2,5)
    imshow(onrf[:,:,cellnumber])
    title("ON")
    xticks([])
    yticks([])
    cbar = colorbar()
    cbar.ax.set_ylabel('(spk/s)', fontsize=8)
    for t in cbar.ax.get_yticklabels():
        t.set_fontsize(8)
    
    subplot(3,2,6)
    imshow(offrf[:,:,cellnumber])
    title("OFF")
    xticks([])
    yticks([])
    cbar = colorbar()
    cbar.ax.set_ylabel('(spk/s)', fontsize=8)
    for t in cbar.ax.get_yticklabels():
        t.set_fontsize(8)
        
    tight_layout()
    suptitle("Cell Number: " + cellnumber, fontsize=14)
    
if __name__=='__main__':
    oridata = r''
    sfdata = r''
    tfdata = r''
    sftfdata = r''
    rfdata = r''
    cellnumber = 
    plotonecell(oridata, sfdata, tfdata, sftfdata, rfdata, cellnumber)
