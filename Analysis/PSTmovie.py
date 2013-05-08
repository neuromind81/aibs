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
from loadlog import loadh5

def PSTmovie(datapath, logpath, syncpath, modality, moviename, subX=None, subY=None):
    '''load stimulus log'''
    print "loading stimulus log from:",logpath    
    (stimuluscondition, sweeplength, _) = getSweepTimesOP(logpath, modality)
    sweeplength = (sweeplength/60)*4
    '''stimuluscondition is sorted on xp, yp and sortcondition'''
    
    '''load h5 movie'''
    print "loading data from:",datapath    
#    f = h5py.File(datapath, 'r')
#    print f.keys()
#    d = f['data']
#    data = d[...]
    data = loadh5(datapath, 'data')
    
    sz0 = size(data,0) #time dimension
    sz1 = size(data,1) #x dimension
    sz2 = size(data,2) #y dimension
    
    data = np.swapaxes(data,0,2)
    data = np.swapaxes(data,0,1)
    
    '''stimuluscondition to synccondition'''
    synccondition = getsync(syncpath, stimuluscondition)
    
    if subX is None:
        subX = stimuluscondition[0,2]
    if subY is None:
        subY = stimuluscondition[0,3]
    print "subX: ", subX
    print "subY: ", subY
    
    '''select specific (subX, subY) region'''
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
        os.system("del", moviename)
    except:
        print moviename + "not found, a new one will be created."

    os.system("ffmpeg -f image2 -i _tmp%05d.png " + moviename)
    os.system("del _tmp*.png")

    return (stimuluscondition, syncsub)

def getsync(syncpath, stimuluscondition):
    '''load sync data'''
    print "loading stimulus sync from:",syncpath
    sync = sio.loadmat(syncpath)
    syncframe = sync['syncframe']
    
    '''stimulus frame to acquisition frame'''
    synccondition = np.zeros((size(stimuluscondition,0),size(stimuluscondition,1)))

    for i in range(len(stimuluscondition)):
        start = stimuluscondition[i,0] + 3
        end = stimuluscondition[i,1] + 3
        temp = []
        temp = np.where(syncframe[0][:] == start)
        synccondition[i,0] = floor(temp[0][0]/256/8)
        temp = []
        temp = np.where(syncframe[0][:] == end)        
        synccondition[i,1] = floor(temp[0][0]/256/8)

    synccondition[:,2:] = stimuluscondition[:,2:]
    return synccondition

def plotmov(movie, condition, frame):
    movieslice = movie[:,:,frame]
    if np.mod(condition[frame],5)>0:
        texttoshow = ''
    else:
        texttoshow = str(int(condition[frame]))+" Deg"     
    imshow(movieslice, cmap="gray",vmin=0, vmax=50)
    xticks([])
    yticks([])
    text(50, 500, texttoshow, fontsize=12, color='white')    

if __name__=='__main__':
    datapath = r'Z:\ImageData\CA203_130425_grating\CA203_130425_grating_ch2_015_Downsampled\Concat\Concat_Downsampled_CA203_130425_grating_ch2_015_f00052.h5'
    logpath = r'Z:\ImageData\CA203_130425_grating\130425120039-CA203_130425_gratings.log'
    syncpath = r'Z:\ImageData\CA203_130425_grating\Ori\Sync\syncdata.mat'
    modality = 'ori'
    moviename = 'CA203_15_Ori_movie.avi'
    subX = -25
    subY = 20
    
    (stimuluscondition, syncsub) = PSTmovie(datapath, logpath, syncpath, modality, moviename, subX, subY)