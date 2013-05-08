# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 16:19:05 2013

@author: saskiad
"""

from pylab import *
import scipy as sp
import scipy.io as sio
import numpy as np
import os
import h5py
from findlevel import *
import sys

def getsync(syncpath, stimuluscondition):
    '''stimuluscondition to synccondition'''
    print "loading stimulus sync from:",syncpath
    sync = sio.loadmat(syncpath)
    syncframe = sync['syncframe']
    syncdata = sync['syncdata']
    del sync

    '''test integrity of sync signal'''
    thr = np.amin(syncdata)+(0.75*(np.ptp(syncdata)))
    temp = findlevels(syncdata, thr, 100, 'both')
    levellen = np.ediff1d(temp, to_begin=temp[0])
    fframe = findlevel(levellen, 256, 'down')
    print "first frame:", fframe
    test = np.where(levellen>256)
    if amax(test) > fframe:
        print "SYNC ERROR!!"
        sys.exit('Problems with the sync data')
    else:
        print "Sync is good!"
    
    '''stimulus frame to acquisition frame'''
    synccondition = np.zeros((size(stimuluscondition,0),size(stimuluscondition,1)))

    for i in range(len(stimuluscondition)):
        start = stimuluscondition[i,0] + fframe
        end = stimuluscondition[i,1] + fframe
        temp = []
        temp = np.where(syncframe[0][:] == start)
        synccondition[i,0] = int(floor(temp[0][0]/256/8))
        temp = []
        temp = np.where(syncframe[0][:] == end)        
        synccondition[i,1] = int(floor(temp[0][0]/256/8))

    synccondition[:,2:] = stimuluscondition[:,2:]
    return synccondition

def OPtraceave(celltraces, starttimes, duration, showflag):
    '''averages continuous waveforms'''
    numcells = len(celltraces)
    numstim = size(starttimes)
    
    traceave = np.empty((duration,numcells),dtype=float)
    tracesem = np.empty((duration,numcells),dtype=float)
      
    temp = np.empty((duration, numstim))
    for ci in range(numcells):        
        for i in range(numstim):
            temp[:,i] = celltraces[ci][starttimes[i]:(starttimes[i]+duration)]
            #fix this when using h5 file
        traceave[:,ci] = temp.mean(1)
        tracesem[:, ci] = temp.std(1)/sqrt(numstim)
    return (traceave, tracesem)

def loaddata(datapath, logpath, syncpath, modality):
    print "loading traces from:", datapath    
    #celltraces = loadh5(datapath, 'data_t')
    celltraces = loadtraces(datapath)
    
    print "loading stimulus log from:",logpath 
    (stimuluscondition, _, _) = getSweepTimesOP(logpath, modality)
    syncc = getsync(syncpath, stimuluscondition)
    
    return (celltraces, stimuluscondition, syncc)
    
def saveh5(savepath, filename, data):
    fullfilename = os.path.join(savepath, filename)
    f = h5py.File(fullfilename)
    dset = f.create_dataset("data", data.shape, 'f')
    dset[...] = data
    f.close()