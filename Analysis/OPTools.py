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


def getsync(syncpath, stimuluscondition):
    '''stimuluscondition to synccondition'''
    print "loading stimulus sync from:",syncpath
    sync = sio.loadmat(syncpath)
    syncframe = sync['syncframe']
    del sync
    
    '''stimulus frame to acquisition frame'''
    synccondition = np.zeros((size(stimuluscondition,0),size(stimuluscondition,1)))

    for i in range(len(stimuluscondition)):
        start = stimuluscondition[i,0] + 3
        end = stimuluscondition[i,1] + 3
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