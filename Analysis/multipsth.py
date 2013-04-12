# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 14:07:55 2012

@author: saskiad
"""
import numpy as np
from pylab import *
from findlevel import *
#import scipy as sp

def multipsth(spiketimes, starttimes, duration, numbins, showflag):
    '''Calculates and plots PSTHs for multiple cells'''
    '''inputs: array of spiketimes (each column = one cell), list of stimulus start times, duration of stimulus
    number of bins for histogram
    Outputs: plots post stimulus time histogram for each cell
    and a .dat file, first column = bin times, subsequent column = psth for each cell.
    '''

    '''loads spiketimes and starttimes'''
    '''only if you call multipsth yourself'''
    #spiketimes = np.loadtxt(spiketimes, dtype=float)
    #starttimes = np.loadtxt(starttimes, dtype=float)

    numcells = size(spiketimes,1)
    numstim = size(starttimes)
    psthraw = np.zeros((numbins,numcells),dtype=float)
    
    for ci in range(0, numcells):
        cellspikes = sort(spiketimes[:,ci])
        '''gets spike times for one cell'''
        cellspikes = cellspikes[np.logical_not(np.isnan(cellspikes))]
        '''deletes the NaNs'''

        output = []
        for t in starttimes:
            output.extend([x - t for x in cellspikes if t <= x < (t + duration)])
        psthraw[:,ci], edges = np.histogram(output, bins=numbins, range=(0.0, duration))        
        '''creates histogram for one cell'''
    
    psthnorm = psthraw / (duration/numbins) / numstim
    '''normalizes histogram by binsize and number of sweeps'''    
    
    A = np.zeros(((size(psthnorm,0)),((numcells+1))),dtype=float)
    A[:,0] = edges[:-1]
    for i in range(1,(numcells+1)):    
        A[:,i] = psthnorm[:,(i-1)]
    '''creates array of PSTHs for each cell'''
  
    '''plots histograms'''
    if showflag==1:
        figure(0)
        for i in range(1,(numcells+1)):  
            subplot((numcells),1,i)
            bar(A[:,0], A[:,i], width=(duration/numbins), bottom=0,)
            xlim(0,duration)
            ylabel('Firing rate (spk/s)')
            tstr = ('Cell No. ', i)
            title(tstr)
        xlabel('Time (s)')
        show()
    
    return A
    
if __name__=='__main__':  
    spikes = 'C:\Users\saskiad\Documents\spiketimes.dat'
    starts = 'C:\Users\saskiad\Documents\starttimes.dat'
    #fileout = 'C:\Users\saskiad\Documents\psth.dat'
    A = multipsth(spikes, starts, 6.0, 75)

