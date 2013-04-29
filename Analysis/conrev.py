# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 14:54:36 2013

@author: saskiad
"""

from pylab import *
import scipy as sp
import numpy as np
from getSweepTimes import *
from loadclu import *
from multipsth import *
from findlevel import *
from flashgrating_NEW import dotuning
import matplotlib.pyplot as plt
import os
import h5py

def conrevEP(datapath, logpath, numbins, showflag):
    '''analysis for contrast reversing e-phys data'''
    print "loading data from:",datapath
    numberofshanks = 8
    '''get data'''    
    (spiketimes, cellnumber) = loadclu(datapath, numberofshanks)
    nc = size(spiketimes,1)
    
    '''get log'''
    modality = 'conrev'
    (stimc, duration, tfreq, constring) = getSweepTimesEPcr(logpath, datapath)
    
    tlabel = "Phase (Deg)"
    ticks = range(0,151,30)
    print tlabel
    print constring
    orivals = np.unique(stimc[:,1])
    orivals = np.delete(orivals, 3, 0)
    for i in range(len(orivals)):
        ostr = str(orivals[i])+"Deg"
        print ostr
        constring = constring + " at " + ostr
        stimuluscondition = stimc[np.where(stimc[:,1] == orivals[i])]
        (tuning, f0m, f0s, f1m, f1s, f2m, f2s) = dotuning(stimuluscondition, spiketimes, cellnumber, 2, duration, tlabel, ticks, constring, ostr, numbins, showflag)
        plotconrev(tuning, f1m, f1s, f2m, f2s, ostr, constring)        
        if i == 0:
            f0mean = np.empty((size(f0m,0), size(f0m,1), len(orivals)))
            f0sem = np.empty((size(f0m,0), size(f0m,1), len(orivals)))
            f1mean = np.empty((size(f2m,0), size(f1m,1), len(orivals)))
            f1sem = np.empty((size(f2m,0), size(f1m,1), len(orivals)))
            f2mean = np.empty((size(f2m,0), size(f2m,1), len(orivals)))
            f2sem = np.empty((size(f2m,0), size(f2m,1), len(orivals)))
        f0mean[:,:,i] = f0m[:,:]
        f0sem[:,:,i] = f0s[:,:]
        f1mean[:,:,i] = f1m[:,:]
        f1sem[:,:,i] = f1s[:,:]  
        f2mean[:,:,i] = f2m[:,:]
        f2sem[:,:,i] = f2s[:,:]
    
    return (tuning, f0mean, f1mean, f2mean, f0sem, f1sem, f2sem)
    
    '''plot data'''
def plotconrev(tuning, f1mean, f1sem, f2mean, f2sem, ostr, constring):
    for s in range(1,9):
        firstcell = findlevelbuffer(cellnumber, s, 100) 
        lastcell = findlevelbuffer(cellnumber, (s+1), 100)
        if lastcell > firstcell:     
            sn = lastcell - firstcell
            print "shank #"+str(s)+" has "+str(sn)+" cells"
            figure(s)        
            for c in range(sn):
                sp = c + firstcell
                ax1 = subplot(ceil(sqrt(sn)), round(sqrt(sn)), c+1)
                ax1.errorbar(tuning, f1mean[:,sp], yerr=f1sem[:,sp], fmt = 'ro', capsize=2, linestyle='-')
                ax1.set_ylabel('F1', color='r', fontsize=10)
                ax1.set_ylim(bottom=0)
                for tl in ax1.get_yticklabels():
                    tl.set_color('r')
                xlabel(tlabel, fontsize=10)
                ax2 = twinx()                
                ax2.errorbar(tuning, f2mean[:,sp], yerr=f2sem[:,sp], fmt = 'bx', capsize=2, linestyle='-')
                ax2.set_ylabel('F2', color='b', fontsize=10)
                ax2.set_ylim(bottom=0)
                for tl in ax2.get_yticklabels():
                    tl.set_color('b')                
                xticks(ticks)             
                xlabel(tlabel, fontsize=10)
                text(0,0, str(c+1), fontsize=10)
                tick_params(axis='both', which='major', labelsize=7)
                tight_layout()
            subplots_adjust(top=0.9)
            suptitle("Shank #"+str(s)+':'+constring, fontsize=14)
            #legend(('f1','mean'),loc=4, prop={'size':10}) 
            fname = datapath+'_'+ostr+'_conrev'+str(s)+'.png'
            savefig(fname)
            show(False)
            
if __name__=='__main__':
    datapath = r''
    logpath = r''
    numbins = 64.0
    showflag = 0
    (tuning, f0mean, f1mean, f2mean, f0sem, f1sem, f2sem) = conrevEP(datapath, logpath, numbins, showflag)