# -*- coding: utf-8 -*-
"""
Created on Wed Apr 03 09:29:24 2013

@author: saskiad
"""
import h5py
from pylab import *
import numpy as np
import scipy.io as sio
from getSweepTimes import getSweepTimesOP
import os, sys
import matplotlib.pyplot as plt

def PSTmovie(datapath, logpath, syncpath, modality, subX, subY):
    '''load stimulus log'''
    print "loading stimulus log from:",logpath    
    (stimuluscondition, sweeplength) = getSweepTimesOP(logpath, modality)
    sweeplength = (sweeplength/60)*4
    '''stimuluscondition is sorted on xp, yp and sortcondition'''
    
    '''load h5 movie'''
    print "loading data from:",datapath    
    f = h5py.File(datapath, 'r')
    print f.keys()
    d = f['data']
    data = d[...]
    
    sz0 = size(data,0) #time dimension
    sz1 = size(data,1) #x dimension
    sz2 = size(data,2) #y dimension
    
    data = np.swapaxes(data,0,2)
    data = np.swapaxes(data,0,1)
    
    '''load sync data'''
    print "loading stimulus sync from:",syncpath
    sync = sio.loadmat(syncpath)
    syncframe = sync['syncframe']
    
    '''stimulus frame to acquisition frame'''
    synccondition = np.zeros((len(stimuluscondition),5))

    for i in range(len(stimuluscondition)):
        start = stimuluscondition[i,0]
        end = stimuluscondition[i,1]
        temp = []
        temp = np.where(syncframe[0][:] == start)
        synccondition[i,0] = floor(temp[0][0]/256/8)
        temp = []
        temp = np.where(syncframe[0][:] == end)        
        synccondition[i,1] = floor(temp[0][0]/256/8)

    synccondition[:,2:] = stimuluscondition[:,2:]
    
    '''select specific region'''
    temp = []
    temp = np.where(np.logical_and(synccondition[:,2]==subX, synccondition[:,3]==subY))
    syncsub = synccondition[temp[0][:]]
    
    '''average same conditions together'''
    valuedifference = np.ediff1d(syncsub[:,4], to_end=None, to_begin = 1)
    transitions = argwhere(valuedifference)
    transitions = append(transitions, len(valuedifference))
    
    conditions = np.zeros(((len(transitions)-1),1))
    temp = np.zeros((sz1, sz2, sweeplength))
    moviecon = []
    contemp = np.empty((sweeplength,1))
    #movie = np.empty((sz2, sz1, (sweeplength*len(conditions))))
    for t in range(len(conditions)):
        conditions[t] = syncsub[transitions[t],4]
    for cond in range(len(conditions)):    
        firstpoint = transitions[cond]
        lastpoint = transitions[cond+1]
        for i in range(firstpoint, lastpoint):
            temp = temp + data[:,:,syncsub[i,0]:(syncsub[i,0]+sweeplength)]
        temp /= (lastpoint-firstpoint+1)
        contemp[:] = conditions[cond]
        if cond == 0:
            movie = temp
        else:
            movie = append(movie, temp, axis=2)
        moviecon = append(moviecon, contemp)
       
    '''put in baselines??'''    
    
    
    '''make movie'''
    print "creating movie"     
    for i in range(size(movie,2)):
        plotmov(movie, moviecon, i)
        fname = '_tmp%05d.png'%i
        plt.savefig(fname)
        plt.clf()
 
    try: 
        os.system("del movie.avi")
    except:
        print "movie.avi not found, a new one will be created."

    os.system("ffmpeg -f image2 -i _tmp%05d.png movie.avi")
    os.system("del _tmp*.png")

    return (stimuluscondition, syncsub)

def plotmov(movie, condition, frame):
    movieslice = movie[:,:,frame]
    texttoshow = str(int(condition[frame])) + " Deg"     
    imshow(movieslice, cmap="gray",vmin=0, vmax=50)
    xticks([])
    yticks([])
    text(50, 500, texttoshow, fontsize=12, color='white')    

if __name__=='__main__':
    datapath = r'C:\Users\saskiad\Documents\Concat_Downsampled_CA153_130307_32X_b_ch2_026_f00026.h5'
    logpath = r'I:\CA153_130307\130307124929-CA153_130307_b.log'
    syncpath = r'I:\CA153_130307\b_syncdata.mat'
    modality = 'ori'
    subX = 25
    subY = 20
    
    (stimuluscondition, syncsub) = PSTmovie(datapath, logpath, syncpath, modality, subX, subY)