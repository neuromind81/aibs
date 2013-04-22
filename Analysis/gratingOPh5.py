# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 14:47:49 2013

@author: saskiad
"""


from pylab import *
import scipy as sp
import numpy as np
import os
from loadlog import *
from getSweepTimes import getSweepTimesOP
from OPTools import *


def gratingOP(datapath, logpath, syncpath, savepath, modality, showflag, subX=None, subY=None):
    '''grating analysis for ori, sf, tf grating stimulus for Optical Imaging'''
    '''modality must be either: 'ori', 'sf', 'tf' '''
    
    '''load data and stimulus information'''    
    print "loading traces from:", datapath    
    #celltraces = loadh5(datapath, 'data_t')
    celltraces = loadtraces(datapath)
    
    print "loading stimulus log from:",logpath 
    (stimuluscondition, sweeplength, constring) = getSweepTimesOP(logpath, modality)
    print constring
    sweeplength = int((sweeplength/60)*4)
    '''stimuluscondition to synccondition'''
    syncc = getsync(syncpath, stimuluscondition)
    
    '''get appropriate subset of stimuli'''
    if subX is None:
        subX = stimuluscondition[0,2]
    if subY is None:
        subY = stimuluscondition[0,3]
    print "subX: ", subX
    print "subY: ", subY

    ang = stimuluscondition[np.nonzero(stimuluscondition[:,4]),4]
    dang = amin(ang)
    
    temp=[]
    temp = np.where(np.logical_and(syncc[:,2]==subX, syncc[:,3]==subY))
    syncsubtemp = syncc[temp[0][:]]
    '''stimuli with stimulus in position (subX, subY)'''
    temp2 = np.where(np.logical_not(mod(syncsubtemp[:,4], dang)))
    syncsub = syncsubtemp[temp2[0][:]]
    '''only conditions with grating - not the inter-sweep interval'''
    
    nc = len(celltraces)
    print "Number of Cells:", nc
    tfreq = 3.0
    
    if (modality.find("sf")+1):
        tlabel = "Spatial frequency (Cyc/Deg)"
        ticks = np.arange(0, 0.62, 0.1)
        print tlabel
        print constring
        sortc = 5
        orivals = np.unique(syncsub[:,4])
        if len(orivals)>3:
            orivals = np.delete(orivals, 3, 0)
        for i in range(len(orivals)):
            synccondition = syncsub[np.where(syncsub[:,4] == orivals[i])]
            ostr = str(orivals[i])+"Deg"            
            print ostr
            (tuning, f0m, f0s) = dotuningOP(synccondition, celltraces, sortc, sweeplength, showflag)
            if i == 0:
                f0mean = np.empty((size(f0m,0), size(f0m,1), len(orivals)))
                f0sem = np.empty((size(f0m,0), size(f0m,1), len(orivals)))
            f0mean[:,:,i] = f0m[:,:]
            f0sem[:,:,i] = f0s[:,:]                
    elif (modality.find("tf")+1):
        tlabel = "Temporal frequency (Cyc/Sec)"
        ticks = range(0,16,3)
        print tlabel
        print constring
        sortc = 6
        orivals = np.unique(syncsub[:,4])
        if len(orivals)>3:
            orivals = np.delete(orivals, 3, 0)
        for i in range(len(orivals)):
            ostr = str(orivals[i])+"Deg"
            synccondition = syncsub[np.where(syncsub[:,4] == orivals[i])]             
            print ostr
            (tuning, f0m, f0s) = dotuningOP(synccondition, celltraces, sortc, sweeplength, showflag)
            if i == 0:
                f0mean = np.empty((size(f0m,0), size(f0m,1), len(orivals)))
                f0sem = np.empty((size(f0m,0), size(f0m,1), len(orivals)))
            f0mean[:,:,i] = f0m[:,:]
            f0sem[:,:,i] = f0s[:,:]            
    elif (modality.find("ori")+1):
        tlabel = "Orientation (Deg)"
        ticks = range(0,361,90)
        print tlabel
        print constring
        sortc = 4
        synccondition = syncsub
        ostr = "allori"
        #constring = constring + " at " + ostr
        (tuning, f0m, f0s) = dotuningOP(synccondition, celltraces, sortc, sweeplength, showflag)
        f0mean = f0m
        f0sem = f0s
    else:
        print "No modality specified"
        
    newpath = os.path.join(savepath, 'Data')
    if os.path.exists(newpath) == False:
        os.mkdir(newpath)
    else:
        print "folder already exists"
        
    '''plot data'''
    for s in range(int(ceil(nc/9))+1):
        firstcell = (s*9)
        lastcell = firstcell+8
        figure(s)
        for c in range(9):
            sp = firstcell + c
            if sp<nc:
                ax1 = subplot(3, 3, c+1)
                if (modality.find("sf")+1) or (modality.find("tf")+1):
#                    ax1.set_xscale('log')
                    ax1.errorbar(tuning, f0mean[:,sp,0], yerr=f0sem[:,sp,0], fmt = 'ro', capsize=2, linestyle='-')
                    ax1.errorbar(tuning, f0mean[:,sp,1], yerr=f0sem[:,sp,1], fmt = 'bo', capsize=2, linestyle='-')
                    ax1.errorbar(tuning, f0mean[:,sp,2], yerr=f0sem[:,sp,2], fmt = 'go', capsize=2, linestyle='-')
                else:
                    ax1.errorbar(tuning, f0mean[:,sp], yerr=f0sem[:,sp], fmt = 'ro', capsize=2, linestyle='-')
                ax1.set_ylabel('Mean DF/F', fontsize=10)
                ax1.set_ylim(bottom=0)
                xlabel(tlabel, fontsize=10)
                xticks(ticks)             
                text(0,0, str(sp+1), fontsize=10)
                tick_params(axis='both', which='major', labelsize=7)
            tight_layout()
        subplots_adjust(top=0.9)
        suptitle(constring + " Cells "+ str(firstcell+1) + " to " + str(lastcell+1), fontsize=14)
        if (modality.find("sf")+1) or (modality.find("tf")+1):
            figtext(0.1, 0.92, '0 Deg', color='red')
            figtext(0.2, 0.92, '120 Deg', color = 'blue')
            figtext(0.3, 0.92, '240 Deg', color = 'green')            
        filename = modality + '_tuning'+str(s)+'.png'
        fullfilename = os.path.join(newpath, filename) 
        savefig(fullfilename)
        if showflag:            
            show(False)
    
    '''save data'''
    filename = modality + "Data.h5"    
    fullfilename = os.path.join(newpath, filename)
    f = h5py.File(fullfilename, 'w')
    dset = f.create_dataset("f0mean", f0mean.shape, 'f')
    dset[...] = f0mean
    dset.attrs["mask"] = (subX, subY)    
    if (modality.find("sf")+1) or (modality.find("tf")+1):     
        dset.attrs["orivalues"] = orivals
    dset.attrs["datapath"] = datapath
    dset.attrs["logpath"] = logpath
    dset.attrs["syncpath"] = syncpath
    dset2 = f.create_dataset("f0sem", f0sem.shape, 'f')
    dset2[...] = f0sem
    dset3 = f.create_dataset("tuning", tuning.shape, 'f')
    dset3[...] = tuning
    f.close()    
    
    return (tuning, f0mean, f0sem)

#def dotuningOP(synccondition, celltraces, sortc, sweeplength, tlabel, ticks, constring, ostr, newpath, showflag):
def dotuningOP(synccondition, celltraces, sortc, sweeplength, showflag):
    nc = len(celltraces)
    print 'Calculating Tuning'    
    
    '''sort sweep times by sort condition'''
    '''difference between values'''
    valuedifference = np.ediff1d(synccondition[:,sortc], to_end=None, to_begin = 1)
    '''indices for condition transitions'''
    transitions = argwhere(valuedifference)    
    transitions = append(transitions, len(valuedifference))
    
    #(f0, f1, f2) = gratingfourierOP(celltraces, synccondition, sweeplength, showflag)
    
    f0mean = np.empty(((len(transitions)-1),nc))
    f0sem = np.empty(((len(transitions)-1),nc))
    tuning = np.zeros(((len(transitions)-1),1))
    
    '''mean +- sem for each same stim condition'''
    for t in range(len(tuning)):
        tuning[t] = synccondition[transitions[t],sortc]    
    for cond in range(len(tuning)):
        firstpoint = transitions[cond]
        lastpoint = transitions[cond+1]
        starttimes = synccondition[firstpoint:lastpoint,0]
        starttimes = starttimes.astype(int32)
        (traceave, tracesem) = OPtraceave(celltraces, starttimes, sweeplength, showflag)     
        f0mean[cond] = traceave.mean(0)
        f0sem[cond] = tracesem.mean(0)
#        temp = f0[firstpoint:lastpoint,:]
#        f0mean[cond,:] = temp.mean(0)
#        f0sem[cond,:] = temp.std(0)/sqrt(lastpoint-firstpoint+1)        
#        temp = f1[firstpoint:lastpoint,:]
#        f1mean[cond,:] = temp.mean(0)
#        f1sem[cond,:] = temp.std(0)/sqrt(lastpoint-firstpoint+1)
#        temp = f2[firstpoint:lastpoint,:]
#        f2mean[cond,:] = temp.mean(0)
#        f2sem[cond,:] = temp.std(0)/sqrt(lastpoint-firstpoint+1)

    return (tuning, f0mean, f0sem)
    

def gratingfourierOP(celltraces, synccondition, sweeplength, showflag):
    nc = len(celltraces) 
    f0 = f1 = f2 = np.zeros((len(synccondition),nc))
    for sweep in range(0,len(synccondition)):
        #tfreq = synccondition[sweep,3]
        tfreq = 3.0/4
        starttimes = np.zeros((tfreq*sweeplength,1))
        for cj in range(0,len(starttimes)):        
            starttimes[cj] = synccondition[sweep,0] + (cj/tfreq)
        (traceave, tracesem) = OPtraceave(celltraces, starttimes, sweeplength, showflag)
        fourier = abs(np.fft.fft(traceave,axis=0))
        freq = np.fft.fftfreq(len(traceave), d=binsize)
        '''fourier analysis'''
        f0[sweep,:] = mean(traceave, axis=0)
        f1[sweep,:] = fourier[argwhere(freq == tfreq)]
        f2[sweep,:] = fourier[argwhere(freq == (2*tfreq))]
        return (f0, f1, f2)
        
if __name__=='__main__':
    datapath = r'I:\CA153_130307\a_raw_traces.mat'
    logpath = r'I:\CA153_130307\130307124033-CA153_130307_a.log'
    syncpath = r'I:\CA153_130307\a_syncdata.mat'
    savepath = r'I:\CA153_130307'
    modality = 'tf'
    showflag = 0
    subX = -25
    subY = 20
    (tuning, f0mean, f0sem) = gratingOP(datapath, logpath, syncpath, savepath, modality, showflag, subX, subY)