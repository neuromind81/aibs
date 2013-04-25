# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 16:00:28 2013

@author: saskiad
"""

from pylab import *
import scipy as sp
import numpy as np
from getSweepTimes import *
from loadclu import *
from multipsth import *
from findlevel import *
import matplotlib.pyplot as plt
import os
import h5py

'''***important***
must indicate which modality is being varied in the given data set, using following code:
    sf = spatial frequency
    tf = temporal frequency
    ori = orientation
    
'''

def flashgrating (datapath, logpath, modality, numbins, showflag):
    '''analysis for EPhys grating experiments including: orientation, spatial frequency or temporal frequency'''
    print "loading data from:",datapath
    numberofshanks = 8
    '''get data'''    
    #sweeptiming = loadsweeptimes(datapath)
    (spiketimes, cellnumber) = loadclu(datapath, numberofshanks)
    nc = size(spiketimes,1)
    
    '''get log'''
    #(sweeporder, sweeptable, bgdimnames) = getSweepTimesEP(logpath)
    (stimc, duration, constring) = getSweepTimesEP(logpath, datapath, modality)    
    
    tfreq = stimc[0,3]  
    
    if (modality.find("sf")+1):
        tlabel = "Spatial frequency (Cyc/Deg)"
        ticks = np.arange(0, 0.62, 0.1)
        print tlabel
        print constring
        orivals = np.unique(stimc[:,1])
        orivals = np.delete(orivals, 3, 0)
        for i in range(len(orivals)):
            stimuluscondition = stimc[np.where(stimc[:,1] == orivals[i])]
            ostr = str(orivals[i])+"Deg"            
            constring = constring + " at " + ostr
            print ostr
            (tuning, f0m, f0s, f1m, f1s, f2m, f2s) = dotuning(stimuluscondition, spiketimes, cellnumber, 2, duration, tlabel, ticks, constring, ostr, numbins, showflag)
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
    elif (modality.find("tf")+1):
        tlabel = "Temporal frequency (Cyc/Sec)"
        ticks = range(0,15,3)
        print tlabel
        print constring
        orivals = np.unique(stimc[:,1])
        orivals = np.delete(orivals, 3, 0)
        for i in range(len(orivals)):
            ostr = str(orivals[i])+"Deg"
            constring = constring + " at " + ostr
            stimuluscondition = stimc[np.where(stimc[:,1] == orivals[i])]
            print ostr
            (tuning, f0m, f0s, f1m, f1s, f2m, f2s) = dotuning(stimuluscondition, spiketimes, cellnumber, 3, duration, tlabel, ticks, constring, ostr, numbins, showflag)
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
    elif (modality.find("ori")+1):
        tlabel = "Orientation (Deg)"
        ticks = range(0,361,90)
        print tlabel
        print constring
        stimuluscondition = stimc
        ostr = "allori"
        (tuning, f0mean, f0sem, f1mean, f1sem, f2mean, f2sem) = dotuning(stimuluscondition, spiketimes, cellnumber, 1, duration, tlabel, ticks, constring, ostr, numbins, showflag)
    else:
        print "No modality specified"
        
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
                ax1 = subplot(ceil(sqrt(sn)), round(sqrt(sn)), c+1)
                if (modality.find("sf")+1) or (modality.find("tf")+1):
                    ax1.set_xscale("log", nonposx='clip')
                    ax1.errorbar(tuning, f1mean[:,sp,0], yerr=f1sem[:,sp,0], fmt = 'ro', capsize=2, linestyle='-')
                    ax1.errorbar(tuning, f1mean[:,sp,1], yerr=f1sem[:,sp,1], fmt = 'bo', capsize=2, linestyle='-')
                    ax1.errorbar(tuning, f1mean[:,sp,2], yerr=f1sem[:,sp,2], fmt = 'go', capsize=2, linestyle='-')
                else:              
                    ax1.errorbar(tuning, f1mean[:,sp], yerr=f1sem[:,sp], fmt = 'ro', capsize=2, linestyle='-')
                ax1.set_ylabel('F1', fontsize=10)
                ax1.set_ylim(bottom=0)
                xticks(ticks)             
                xlabel(tlabel, fontsize=10)
                text(0,0, str(c+1), fontsize=10)
                tick_params(axis='both', which='major', labelsize=7)
                tight_layout()
            subplots_adjust(top=0.9)
            suptitle("Shank #"+str(s)+':'+constring, fontsize=14)
            if (modality.find("sf")+1) or (modality.find("tf")+1):
                figtext(0.1, 0.92, '0 Deg', color='red')
                figtext(0.2, 0.92, '120 Deg', color = 'blue')
                figtext(0.3, 0.92, '240 Deg', color = 'green')
            fname = datapath+'_'+modality+'_tuning'+str(s)+'.png'
            savefig(fname)
            show(False)
    
    '''save data'''
    fullfilename = datapath + "_" + modality + "Data.h5"    
    f = h5py.File(fullfilename, 'w')
    dset = f.create_dataset("f0mean", f0mean.shape, 'f')
    dset[...] = f0mean
    if (modality.find("sf")+1) or (modality.find("tf")+1):  
        dset.attrs["orivalues"] = orivals
    dset.attrs["datapath"] = datapath
    dset.attrs["logpath"] = logpath
    dset2 = f.create_dataset("f0sem", f0sem.shape, 'f')
    dset2[...] = f0sem
    dset3 = f.create_dataset("f1mean", f1mean.shape, 'f')
    dset3[...] = f1mean
    dset4 = f.create_dataset("f1sem", f1sem.shape, 'f')
    dset4[...] = f1sem
    dset5 = f.create_dataset("tuning", tuning.shape, 'f')
    dset5[...] = tuning
    dset6 = f.create_dataset("cellnumber", cellnumber.shape, 'f')
    dset6[...] = cellnumber
    f.close()    

    
    return (cellnumber, tuning, f0mean, f0sem, f1mean, f1sem, f2mean, f2sem)

    
def dotuning(stimuluscondition, spiketimes, cellnumber, sortc, duration, tlabel, ticks, constring, ostr, numbins, showflag):
    nc = size(spiketimes,1)
    
    '''sort sweep times by sort condition'''
    '''difference between values'''
    valuedifference = np.ediff1d(stimuluscondition[:,sortc], to_end=None, to_begin = 1)
    '''indices for condition transitions'''
    transitions = argwhere(valuedifference)    
    #transitions = append(transitions, len(valuedifference))
    
    (f0, f1, f2) = gratingfourier(spiketimes, stimuluscondition, duration, numbins, showflag)    
    
    f0mean = np.zeros(((len(transitions)-1),nc))
    f0sem = np.zeros(((len(transitions)-1),nc))
    f1mean = np.zeros(((len(transitions)-1),nc))
    f1sem = np.zeros(((len(transitions)-1),nc))
    f2mean = np.zeros(((len(transitions)-1),nc))
    f2sem = np.zeros(((len(transitions)-1),nc))
    tuning = np.zeros(((len(transitions)-1),1))
    '''mean +- sem for each same stim condition'''
    for t in range(len(tuning)):
        tuning[t] = stimuluscondition[transitions[t],sortc]    
    for cond in range(len(tuning)):
        firstpoint = transitions[cond]
        lastpoint = transitions[cond+1]
        temp = f0[firstpoint:lastpoint,:]
        f0mean[cond,:] = temp.mean(0)
        f0sem[cond,:] = temp.std(0)/sqrt(lastpoint-firstpoint+1)        
        temp = f1[firstpoint:lastpoint,:]
        f1mean[cond,:] = temp.mean(0)
        f1sem[cond,:] = temp.std(0)/sqrt(lastpoint-firstpoint+1)
        temp = f2[firstpoint:lastpoint,:]
        f2mean[cond,:] = temp.mean(0)
        f2sem[cond,:] = temp.std(0)/sqrt(lastpoint-firstpoint+1)
    
    return (tuning, f0mean, f0sem, f1mean, f1sem, f2mean, f2sem)  

def gratingfourier(spiketimes, stimuluscondition, duration, numbins, showflag):
    nc = size(spiketimes,1)    
    f0 = np.zeros((len(stimuluscondition),nc))    
    f1 = np.zeros((len(stimuluscondition),nc))
    f2 = np.zeros((len(stimuluscondition),nc))
    for sweep in range(0,len(stimuluscondition)):
        tfreq = stimuluscondition[sweep,3]       
        starttimes = np.zeros((tfreq*duration,1))
        for cj in range(0,len(starttimes)):        
            starttimes[cj] = stimuluscondition[sweep,0] + (cj/tfreq)
        binsize = (1/tfreq)/numbins
        spikepsth = multipsth(spiketimes, starttimes, (1/tfreq), numbins, showflag)
        '''makes psth for each cell per sweep'''
        temp1 = delete(spikepsth,0,1)
        #deletes the bintimes, just the psths remain
        fourier = abs(np.fft.fft(temp1,axis=0))
        freq = np.fft.fftfreq(len(temp1), d=binsize)
        '''fourier analysis'''
        f0[sweep,:] = mean(temp1, axis=0)
        f1[sweep,:] = fourier[argwhere(freq == tfreq)]
        f2[sweep,:] = fourier[argwhere(freq == (2*tfreq))]
        #what are the units that the fft returns?
    return(f0, f1, f2)


if __name__ == '__main__':
    datapath = r"C:\Users\saskiad\Documents\ephys\20130228_M10_Ori4\20130228_M10_Ori4"
    logpath = r"C:\Users\saskiad\Documents\ephys\ORI4\130228134828-M10.log"
    numbins = 64.0
    showflag = 0
    modality = 'ori'
    #binsize as 128 bins per stimulus cycle?
    (cellnumber, tuning, f0mean, f0sem, f1mean, f1sem, f2mean, f2sem) = flashgrating (datapath, logpath, modality, numbins, showflag)


