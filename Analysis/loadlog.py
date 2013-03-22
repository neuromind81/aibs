# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 09:32:07 2013

@author: saskiad
"""

import scipy as sp
import scipy.io as sio
import numpy as np
from findlevel import findlevels, findlevelsdown

def loadsweep(datapath):
    '''loads sweep and diode data'''
    '''old version based on output from Jay's Matlab algorithm'''
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
    '''loads stimulus log'''
    log = sio.loadmat(logpath)
    sweeplist = log['bgsweeporder'].tolist()
    sweeporder = [int(l[0]) for l in sweeplist]
    #logtemp = log['bgsweeptable'][0][0].tolist()
    logtemp = log['bgsweeptable'].tolist()
    dimnames = log['bgdimnames'].tolist()
    return (sweeporder, logtemp, dimnames)
    
def loadsweeptimes(path):
    '''loads sweep timing correcteced for computer - monitor delay'''
    datapath = path + ".dat"
    metapath = path + ".meta"
    d = open(datapath)
    data = np.fromfile(d,np.int16)
    m = open(metapath)
    meta = m.readlines()
    
    channels = int(meta[7].split(' = ')[1])
    samplerate = int(meta[10].split(' = ')[1])
    duration = len(data)/channels/samplerate
    
    datareshaped = np.transpose(np.reshape(data,(len(data)/channels,channels)))
    
    sweeptrace = datareshaped[(channels-3),:]
    vsynctrace = datareshaped[(channels-2),:]
    diodetrace = datareshaped[(channels-1),:]
    
    #sweep start and end times   
    sweep = findlevels(sweeptrace, 4000, 80000)
    sweep = np.column_stack([sweep, findlevelsdown(sweeptrace, -4000, 80000)])
    
    vsync = findlevelsdown(vsynctrace, -4000, 300)
    
    diode = findlevels(diodetrace, 200, 600)
    diode = np.append(diode, findlevelsdown(diodetrace, 200, 600))
    diode.sort()
    diode = np.delete(diode,[0,1],0)
    
    #corrects for delay between computer and monitor
    sweep -= (vsync[0]-diode[0])
    #converts to time
    sweeptiming = sweep + 0.0
    sweeptiming /= 20000    
    return sweeptiming
 

#path = r"C:\Users\saskiad\Documents\ephys\20130228_M10_Ori4\20130228_M10_Ori4"

#sweeptest = loadsweeptimes(path)