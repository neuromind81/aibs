# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 16:00:22 2013

@author: saskiad
"""
import h5py
import matplotlib
from pylab import *
import scipy as sp
import numpy as np
from loadlog import *
from getSweepTimes import *
from findlevel import findlevel
import matplotlib.pyplot as plt
import matplotlib.animation as manimation

def maprfOP(datapath, logpath, syncpath, savepath, showflag):
    print "loading traces from:", datapath    
    #celltraces = loadh5(datapath, 'data_t')
    celltraces = loadtraces(datapath)
    nc = len(celltraces)
    
    print "loading stimulus log from:",logpath
    (sweeporder, sweeptable, bgdimnames, sweeptiming) = getSweepTimesEPrf(logpath)

    '''arranges stimulus conditions'''    
    stimuluscondition = np.zeros((len(sweeporder),5))
    stimuluscondition[:,0:1] = sweeptiming[:,:]
    for i in range(0, len(sweeporder)):    
        j = sweeporder[i]        
        stimuluscondition[i,2] = sweeptable[j][bgdimnames.index('Color')]
        stimuluscondition[i,3] = sweeptable[j][bgdimnames.index('PosX')]
        stimuluscondition[i,4] = sweeptable[j][bgdimnames.index('PosY')]
    stimuluscondition = stimuluscondition[np.lexsort((stimuluscondition[:,4], stimuluscondition[:,3], stimuluscondition[:,2]))]
    
    syncc = getsync(syncpath, stimuluscondition)
    
    '''number of xpositions and ypositions'''
    nxp = ((amax(syncc[:,3])-amin(syncc[:,3]))/5)+1
    nyp = ((amax(syncc[:,4])-amin(syncc[:,4]))/5)+1
    
    '''on and off count maps'''
    offrf = np.zeros((nxp,nyp,nc))
    #offcount = np.zeros((nxp,nyp))
    onrf = np.zeros((nxp,nyp,nc))
    #oncount = np.zeros((nxp,nyp))
    
    '''difference between values'''
    valuedifference = np.ediff1d(syncc[:,4], to_end=None, to_begin = 1)
    '''indices for condition transitions'''
    transitions = argwhere(valuedifference)    
    transitions = append(transitions, len(valuedifference))
    
    sweeplength = syncc[0,1]-syncc[0,0]
    for cond in range(len(transitions)):
        firstpoint = transitions[cond]
        lastpoint = transitions[cond+1]
        starttimes = syncc[firstpoint:lastpoint,0]
        starttimes = starttimes.astype(int32)
        (traceave, tracesem) = OPtraceave(celltraces, starttimes, sweeplength, showflag)     
        #f0mean[cond] = traceave.mean(0)
        #f0sem[cond] = tracesem.mean(0)
        xp = (syncc[firstpoint,3]-amin(syncc[:,3]))/5
        yp = (syncc[firstpoint,4]-amin(syncc[:,4]))/5            
        if synnc[firstpoint,0] == -1:
            offrf[xp,yp,:] = traceave.mean(0)
            offsem[xp,yp,:] = tracesem.mean(0)
        if synnc[firstpoint,0] == 1:
            onrf[xp,yp,:] = traceave.mean(0)
            onsem[xp,yp,:] = tracesem.mean(0)
    
    newpath = os.path.join(savepath, 'RFData')
    if os.path.exists(newpath) == False:
        os.mkdir(newpath)
    else:
        print "folder already exists"    
    
    '''plot data'''
    for s in range(int(ceil(nc/4))+1):
        firstcell = (s*4)
        lastcell = firstcell+3
        figure(s)
        for c in range(4):
            sp = firstcell + c
            if sp < nc:
                for ci in range(3):                    
                    subplot(4,4,(4*c)+1+ci)
                    if np.logical_not(mod(c,2)):                    
                        imshow(onrf[:,:,sp/2])
                        title("ON")
                    else:
                        imshow(offrf[:,:,sp/2])
                        title("OFF")
                    xticks([])
                    yticks([])
                    tight_layout()
                    text(0,0, str(int(floor(sp/2)+1)), fontsize=10, color='white')
                    cbar = colorbar()
                    cbar.ax.set_ylabel('DF/F', fontsize=8)
                    for t in cbar.ax.get_yticklabels():
                        t.set_fontsize(8)
                subplots_adjust(top=0.9)
                suptitle(constring + " Cells "+ str(firstcell+1) + " to " + str(lastcell+1), fontsize=14)
                fname = newpath + '_RF' + str(s) + '.png'
                savefig(fname)
                if showflag:
                    show(False)
    
    '''save data'''
    fullfilename = newpath + '_RFData.h5'
    f = h5py.File(fullfilename)
    dset = f.create_dataset("offRF", offrf.shape, 'f')
    dset[...] = offrf
    dset.attrs["NumberPositions"] = (nxp, nyp)
    dset.attrs["datapath"] = datapath
    dset.attrs["logpath"] = logpath
    dset.attrs["syncpath"] = syncpath
    dset2 = f.create_dataset("onRF", onrf.shape, 'f')
    dset2[...]=onrf
    f.close()
    
    return (onrf, offrf)

if __name__=='__main__':
    datapath = r''
    logpath = r''
    syncpath = r''
    savepath = r''
    showflag = 1
    (onrf, offrf) = (datapath, logpath, syncpath, savepath, showflag)
    