# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 11:18:58 2013

@author: saskiad
"""

from pylab import *
import scipy as sp
import numpy as np
import os
from loadlog import *
from getSweepTimes import getSweepTimesOP
from OPTools import *

def sftfOP(datapath, logpath, syncpath, savepath, showflag, subX=None, subY=None):
    '''SF X TF stimulus analysis for Optical Imaging'''    
    '''load data and stimulus information'''    
    print "loading traces from:", datapath    
    #celltraces = loadh5(datapath, 'data_t')
    celltraces = loadtraces(datapath)
    
    print "loading stimulus log from:",logpath 
    (stimuluscondition, sweeplength, _) = getSweepTimesOP(logpath, 'sftf')
    sweeplength = int((sweeplength/60)*4)
    '''stimuluscondition to synccondition'''
    syncc = getsync(syncpath, stimuluscondition)
    
    '''select appropriate subset of sweeps'''
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
    
    '''tuning for each orientation'''
    orivals = np.unique(syncsub[:,4])
    if len(orivals)>3:
        orivals = np.delete(orivals, 3, 0)
    f0mean = np.zeros((3,3,nc,3))
    f0sem = np.zeros((3,3,nc,3))
    for i in range(len(orivals)):
        synccondition = syncsub[np.where(syncsub[:,4] == orivals[i])]       
        ostr = str(int(orivals[i]))
        (f0m, f0s) = sftfOPtuning(synccondition, celltraces, sweeplength, showflag)
        f0mean[:,:,:,i] = f0m
        f0sem[:,:,:,i] = f0s
    
    newpath = os.path.join(savepath, 'SFTFData')
    if os.path.isdir(newpath) == False:
        os.mkdir(newpath)
    elif os.path.exists(newpath) == True:
        print "folder already exists"
    
    '''make figures'''
    for s in range(int(ceil(nc/4))+1):
        firstcell = (s*4)
        lastcell = firstcell+3
        figure(s)
        for c in range(4):
            sp = firstcell + c
            if sp < nc:
                for ci in range(3):                    
                    subplot(4,4,(3*c)+1+ci)
                    #set_xscale('log')
                    #set_yscale('log')
                    imshow(f0mean[:,:,sp,ci], origin='lower',cmap='gray')
                    text(0,0, str(sp+1), fontsize=7, color='white')
                    xlabel('TF (Cyc/Sec)', fontsize=10)
                    ylabel('SF (Cyc/Deg)', fontsize=10)
                    xticks(range(3), ['1', '4', '15'])
                    yticks(range(3), ['0.05','0.1','0.2'])
                    tick_params(axis='both', which='major', labelsize=7)
                    tight_layout()                
                    cbar = colorbar()
                    cbar.ax.set_ylabel('Mean dF/F', fontsize=8)
                    for t in cbar.ax.get_yticklabels():
                        t.set_fontsize(8)
            subplots_adjust(top=0.9)
        suptitle("Cells "+ str(firstcell+1) + " to " + str(lastcell+1), fontsize=14)
        figtext(0.2, 0.92,'0 Deg')
        figtext(0.5, 0.92, '120 Deg')
        figtext(0.8, 0.92, '240 Deg')
        filename = 'sftf_tuning' + str(s) + '.png'            
        fullfilename = os.path.join(newpath, filename) 
        savefig(fullfilename)
        if showflag:            
            show(False)
    
    '''save data'''    
#    saveh5(savepath, 'sftf_f0mean.h5', f0mean)
#    saveh5(savepath, 'sftf_f0sem.h5', f0sem)
    fullfilename = os.path.join(newpath, "sftfData.h5")
    f = h5py.File(fullfilename, 'w')
    dset = f.create_dataset("f0mean", f0mean.shape, 'f')
    dset[...] = f0mean
    dset.attrs["mask"] = (subX, subY)
    dset.attrs["orivalues"] = orivals
    dset.attrs["datapath"] = datapath
    dset.attrs["logpath"] = logpath
    dset.attrs["syncpath"] = syncpath
    dset2 = f.create_dataset("f0sem", f0sem.shape, 'f')
    dset2[...]=f0sem
    f.close()

    return(f0mean, f0sem, syncc)
        

def sftfOPtuning(syncsub, celltraces, sweeplength, showflag):
    nc = len(celltraces)    

    f0mean = np.zeros((3,3,nc))
    f0sem = np.zeros((3,3,nc))
    
    '''sort sweep times by sort condition'''
    '''difference between values'''
    valuedifference = np.ediff1d(syncsub[:,6], to_end=None, to_begin = 1)
    '''indices for condition transitions'''
    transitions = argwhere(valuedifference)    
    transitions = append(transitions, len(valuedifference))
    
    f0m = np.empty(((len(transitions)-1),nc))
    f0s = np.empty(((len(transitions)-1),nc))      
    for cond in range(len(transitions)-1):
        firstpoint = transitions[cond]
        lastpoint = transitions[cond+1]
        starttimes = syncsub[firstpoint:lastpoint,0]
        starttimes = starttimes.astype(int32)
        (traceave, tracesem) = OPtraceave(celltraces, starttimes, sweeplength, showflag)     
        sp = int(floor(10*syncsub[firstpoint, 5]))
        tp = int(sqrt(syncsub[firstpoint,6])-1)        
        f0mean[sp,tp,:] = traceave.mean(0)
        f0sem[sp,tp,:] = tracesem.mean(0)
        
    return (f0mean, f0sem)

if __name__=='__main__':
    datapath = r'I:\CA153_130307\h32_raw_traces.mat'
    logpath= r'I:\CA153_130307\130307131711-CA153_130307_h.log'
    syncpath = r'I:\CA153_130307\h_syncdata.mat'
    savepath = r'I:\CA153_130307'
    subX = -25
    subY = 20
    showflag = 0
    (f0mean, f0sem, synccondition) = sftfOP(datapath, logpath, syncpath, savepath, showflag, subX, subY)