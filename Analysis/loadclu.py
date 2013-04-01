# -*- coding: utf-8 -*-
"""
Created on Wed Feb 06 15:14:36 2013

@author: saskiad
"""
from pylab import *
import scipy as sp
import scipy.io as sio
import numpy as np
from findlevel import *

def loadclu(path, numberoffiles):
    for i in range(1,(numberoffiles+1)):
        cluin = path +'.clu.' + str(i)
        resin = path + '.res.' + str(i)
        celllist = np.loadtxt(cluin, dtype = int)
        celllist = delete(celllist,0)
        timelist = np.loadtxt(resin, dtype = int)
        
        '''puts data into an array, column 0 = cell#, column1 = spike bin'''
        spikearray = np.column_stack([celllist, timelist])
        
        '''sorts by cell#'''
        spikearray = spikearray[spikearray[:,0].argsort()]
        spikearray = np.delete(spikearray,len(spikearray)-1,0)
    
        if i == 1:
            nc = size(celllist)
            spikelistlong = np.zeros((nc,0))
            cellnumber = np.zeros((0))
    
        '''array where each column contains the spike times for a single cell'''
        spikelisttemp = np.zeros((nc,(max(spikearray[:,0])-1)), dtype = float)
        for k in range(2,(max(spikearray[:,0]+1))):
            temp = np.argwhere(spikearray[:,0]==k)
            for j in range(0,len(temp)):    
                spikelisttemp[j,(k-2)] = spikearray[temp[j],1]
            cn = float(i + (float(k)/100))
            cellnumber = np.append(cellnumber,cn)
       
        '''appends cells from one file to array of all files'''
        spikelistlong = np.append(spikelistlong, spikelisttemp,1)    
    
    '''trims list of extra 0s'''
    temp2 = np.argwhere(spikelistlong)
    cut = range(max(temp2[:,0])+1, len(spikelistlong)+1)
    spikelist = np.delete(spikelistlong,cut,0)
    
    '''convert extra 0s to Nan'''
    for yi in range(0,size(spikelist,axis=1)):
        if spikelist[len(spikelist)-1,yi] == 0:
            xi = findleveldown(spikelist[:,yi],0)
            for i in range(xi,len(spikelist)):
                spikelist[i,yi] = nan

    '''sampled at 20kHz, from bin number to seconds'''
    spikelist += 0.0    
    spikelist/=20000
    
    return (spikelist, cellnumber)

if __name__ == '__main__':
    path = r"C:\Users\saskiad\Documents\ephys\20130228_M10_Ori4\20130228_M10_Ori4"
    numberoffiles = 8
    (spikelist, cellnumber) = loadclu(path, numberoffiles)