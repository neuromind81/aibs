# -*- coding: utf-8 -*-
"""
Created on Tue Apr 09 14:27:24 2013

@author: saskiad
"""
from pylab import *
import scipy as sp
import numpy as np
from getSweepTimes import *
from loadclu import *
#from multipsth import *
from findlevel import *
from flashgrating import gratingfourier
import matplotlib.pyplot as plt


def sftf(datapath, logpath, numbins, showflag):
    '''analysis for spatial frequency X temporal frequency X orientation stimulus'''
    print "loading data from:",datapath
    numberofshanks = 8
    '''get data'''    
    (spiketimes, cellnumber) = loadclu(datapath, numberofshanks)
    nc = size(spiketimes,1)
    
    '''get log'''
    (stimc, duration, constring) = getSweepTimesEP(logpath, datapath, 'sftf')
    
    orivals = np.unique(stimc[:,1])
    orivals = np.delete(orivals, 3, 0)
    for i in range(len(orivals)):
        stimuluscondition = stimc[np.where(stimc[:,1] == orivals[i])]
        ostr = str(orivals[i])+"Deg"            
        constring = constring + " at " + ostr
        (f0mean, f0sem, f1mean, f1sem, f2mean, f2sem) = sftftuning(stimuluscondition, spiketimes, cellnumber, 3, duration, constring, ostr, numbins, showflag)
    return (cellnumber, f0mean, f0sem, f1mean, f1sem, f2mean, f2sem)

def sftftuning(stimuluscondition, spiketimes, cellnumber, sortc, duration, constring, ostr, numbins, showflag):
    nc = size(spiketimes,1)
    
    '''sort sweep times by sort condition'''
    '''difference between values'''
    valuedifference = np.ediff1d(stimuluscondition[:,sortc], to_end=None, to_begin = 1)
    '''indices for condition transitions'''
    transitions = argwhere(valuedifference)          
    transitions = append(transitions, len(valuedifference))

    (f0, f1, f2) = gratingfourier(spiketimes, stimuluscondition, duration, numbins, showflag)    
    
    f0mean = np.zeros((3,3,nc))
    f0sem = np.zeros((3,3,nc))
    f1mean = np.zeros((3,3,nc))
    f1sem = np.zeros((3,3,nc))
    f2mean = np.zeros((3,3,nc))
    f2sem = np.zeros((3,3,nc))
    #tuning = np.zeros((3,3,1))
    
    for cond in range(len(transitions)-1):
        firstpoint = transitions[cond]
        lastpoint = transitions[cond+1]
        sp = int(floor(10*stimuluscondition[firstpoint, 2]))
        tp = int(sqrt(stimuluscondition[firstpoint,3]))
        temp = f0[firstpoint:lastpoint,:]
        f0mean[sp,tp,:] = temp.mean(0)
        f0sem[sp,tp,:] = temp.std(0)/sqrt(lastpoint-firstpoint+1)        
        temp = f1[firstpoint:lastpoint,:]
        f1mean[sp,tp,:] = temp.mean(0)
        f1sem[sp,tp,:] = temp.std(0)/sqrt(lastpoint-firstpoint+1)
        temp = f2[firstpoint:lastpoint,:]
        f2mean[sp,tp,:] = temp.mean(0)
        f2sem[sp,tp,:] = temp.std(0)/sqrt(lastpoint-firstpoint+1)
    
    '''plot data'''
    for s in range(1,9):
        firstcell = findlevelbuffer(cellnumber, s, 100) 
        lastcell = findlevelbuffer(cellnumber, (s+1), 100)
        if lastcell > firstcell:     
            sn = lastcell - firstcell
            print "shank #"+str(s)+" has "+str(sn)+" cells"
            figure(s)
            for c in range(sn):
                sp = c + firstcell
                subplot(ceil(sqrt(sn)), round(sqrt(sn)), c+1)
                #set_xscale('log')
                #set_yscale('log')
                imshow(f1mean[:,:,sp], origin='lower',cmap='gray')
                #set_xscale('log')
                #set_yscale('log')
                xticks(range(3), ['1', '4', '15'])
                yticks(range(3), ['0.05','0.1','0.2'])
                xlabel('TF (Cyc/Sec)', fontsize=10)
                ylabel('SF (Cyc/Deg)', fontsize=10)
                text(0,0, str(c+1), fontsize=10, color='white')
                tick_params(axis='both', which='major', labelsize=7)
                tight_layout()                
                cbar = colorbar()
                cbar.ax.set_ylabel('F1', fontsize=8)
                for t in cbar.ax.get_yticklabels():
                    t.set_fontsize(8)
            subplots_adjust(top=0.9)
            suptitle("Shank #"+str(s)+':'+constring, fontsize=14)
            fname = datapath+'_'+ostr+'_tuning'+str(s)+'.png'
            savefig(fname)
            show(False)
    
    return (f0mean, f0sem, f1mean, f1sem, f2mean, f2sem)        

if __name__ == '__main__':
    datapath = r"E:\CLUtoANALYZE25mars2013\SFxTFs\M14\2013_03_14_M14_SFxTF1"
    logpath = r"E:\CLUtoANALYZE25mars2013\M14logs\SFxTF1\130314155625-M14.log"
    numbins = 64.0
    showflag = 0
    #binsize as 128 bins per stimulus cycle?
    (cellnumber, f0mean, f0sem, f1mean, f1sem, f2mean, f2sem) = sftf(datapath, logpath, numbins, showflag)
    