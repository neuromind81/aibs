# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 09:32:07 2013

@author: saskiad
"""

import scipy as sp
import scipy.io as sio
import numpy as np
import h5py
from findlevel import *
import sys


    
def loadsweeptimes(path):
    '''loads sweep timing corrected for computer - monitor delay'''
    datapath = path + ".dat"
    metapath = path + ".meta"
    
    channels,_ = loadmeta(metapath)
#    m = open(metapath)
#    meta = m.readlines()
#    
#    channels = int(meta[7].split(' = ')[1])
    #samplerate = int(meta[10].split(' = ')[1])
    #duration = len(data)/channels/samplerate
    
    data = loadbinary(datapath, channels=channels)
    sweeptrace = np.array(data[:, (channels-3)])
    vsynctrace = np.array(data[:, (channels-2)])
    diodetrace = np.array(data[:, (channels-1)])    
    d = open(datapath)
#    data = np.fromfile(d,np.int16)    
#    datareshaped = np.transpose(np.reshape(data,(len(data)/channels,channels)))
#    del data
#    
#    sweeptrace = datareshaped[(channels-3),:]
#    vsynctrace = datareshaped[(channels-2),:]
#    diodetrace = datareshaped[(channels-1),:]
#    del datareshaped    
    
    #sweep start and end times
    sthr = np.ptp(sweeptrace)/4
    sweepup = findlevels(sweeptrace, sthr, 40000, 'up')
    sweepdown = findlevels(sweeptrace, (-1*sthr), 40000, 'down')
    if sweepdown[0] > sweepup[0]:
        if len(sweepup) > len(sweepdown):
            sweep = np.column_stack([sweepup[:-1], sweepdown])
        else:
            sweep = np.column_stack([sweepup, sweepdown])
    elif sweepdown[0] <= sweep[0]:
        sweep = np.column_stack([sweepup, sweepdown[1:]])
    
    vthr = -1*(np.ptp(vsynctrace)/5)
    vsync = findlevels(vsynctrace, vthr, 300, 'up')
    
    dthr = np.ptp(diodetrace)/4    
    diode = findlevels(diodetrace, dthr, 200, 'both')
    #diode = np.reshape(diode, (len(diode)/2, 2))
    diode = np.delete(diode,[0,1],0)
    
    #corrects for delay between computer and monitor
    delay = vsync[0] - diode[0] + 0.0
    print "***Monitor lag:", (delay/20000)
    if delay > 0:
        print "ERROR: diode before vsync"
        sys.exit('diode error')
    sweep -= delay
    #converts to time in seconds
    sweeptiming = sweep + 0.0
    sweeptiming /= 20000    
    return sweeptiming
    
def loadsweeptimesnogap(path):
    '''loads sweep timing corrected for computer - monitor delay'''
    datapath = path + ".dat"
    metapath = path + ".meta"
    
    channels,_ = loadmeta(metapath)
#    m = open(metapath)
#    meta = m.readlines()
#    
#    channels = int(meta[7].split(' = ')[1])
#    #samplerate = int(meta[10].split(' = ')[1])
#    #duration = len(data)/channels/samplerate
    
    data = loadbinary(datapath, channels=channels)
    sweeptrace = np.array(data[:, (channels-3)])
    vsynctrace = np.array(data[:, (channels-2)])
    diodetrace = np.array(data[:, (channels-1)])
#    d = open(datapath)
#    data = np.fromfile(d,np.int16)    
#    datareshaped = np.transpose(np.reshape(data,(len(data)/channels,channels)))
#    del data
#    
#    sweeptrace = datareshaped[(channels-3),:]
#    vsynctrace = datareshaped[(channels-2),:]
#    diodetrace = datareshaped[(channels-1),:]
#    del datareshaped   
    
    temp = findlevel(sweeptrace, 4000, 'up')
    sthr = -1*(np.ptp(sweeptrace)/4)    
    sweep = findlevels(sweeptrace, sthr, 3000, 'up')
    sweep = insert(sweep, 0, temp)
    sweep = delete(sweep, len(sweep)-1, 0)
    sweepdown = findlevels(sweeptrace, sthr, 3000, 'down')
    if len(sweepdown) > len(sweep):
        sweepdown = delete(sweepdown, len(sweepdown)-1, 0)
    sweep = np.column_stack([sweep, sweepdown])
    
    vthr = -1*(np.ptp(vsynctrace)/5)
    vsync = findlevels(vsynctrace, vthr, 300, 'up')
    
    dthr = np.ptp(diodetrace)/4    
    diode = findlevels(diodetrace, dthr, 200, 'both')
    #diode = np.reshape(diode, (len(diode)/2, 2))
    diode = np.delete(diode,[0,1],0)
    #corrects for delay between computer and monitor
    delay = vsync[0] - diode[0] + 0.0
    print "***monitor lag:", (delay/20000)
    if delay > 0:
        print "ERROR: diode before vsync"
        sys.exit('diode error')
    sweep -= delay
    #converts to time
    sweeptiming = sweep + 0.0
    sweeptiming /= 20000    
    return sweeptiming

def loadtraces(matpath):
    '''loads raw OP cell traces from .mat file'''
    mat = sio.loadmat(matpath)
    traces = mat['cell_traces_raw'].tolist()
    return traces

def loadh5(datapath, name):   
    f = h5py.File(datapath, 'r')
    d = f[name]
    data = d[...]
    return data
    
def loadbinary(path, channels = 1, dtype = np.int16):  
    f = open(path)
    data = np.fromfile(f,dtype)
    size = len(data)
    del data
    f.close()
    print "Data length:", size
    print "Channels:",channels

    data = np.memmap(path, dtype=dtype,mode='r',shape=((size/channels),channels))
    return data

def loadmeta(path):
    m = open(path)
    meta = m.readlines()
    channels = int(meta[7].split(' = ')[1])
    samplerate = int(meta[10].split(' = ')[1])
    
#    for item in meta:
#        print item.strip()
    return channels, samplerate

def loadsweep(datapath):
    '''loads sweep and diode data - old version based on output from Jay's Matlab algorithm'''
    mat = sio.loadmat(datapath)
    temp = mat['T'][0][0].tolist()
    frametiming = temp[0]
    sweeptiming = temp[1]
    diodetiming = temp[2]
    spiketiming = temp[3]
    #spiketiming[:,1] = temp[3]
    sweeptiming -= (frametiming[0] - diodetiming[0])
    '''corrects for delay between computer and monitor?'''
    sweeptiming += 0.0
    sweeptiming /= 20000
    return (sweeptiming, spiketiming)
    
def loadlog(logpath):
    '''loads stimulus log - old version using .mat file'''
    log = sio.loadmat(logpath)
    sweeplist = log['bgsweeporder'].tolist()
    sweeporder = [int(l[0]) for l in sweeplist]
    #logtemp = log['bgsweeptable'][0][0].tolist()
    logtemp = log['bgsweeptable'].tolist()
    dimnames = log['bgdimnames'].tolist()
    return (sweeporder, logtemp, dimnames)
 
if __name__ == '__main__':
    datapath = r"E:\CLUtoANALYZE25mars2013\SPANOIs\M14\2013_03_14_M14_SPARSE1"
    sweeptest = loadsweeptimesnogap(datapath)