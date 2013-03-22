# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 15:15:32 2013

@author: saskiad
"""
import matplotlib
from pylab import *
import scipy as sp
import numpy as np
from loadlog import *
from findlevel import findlevel
import matplotlib.pyplot as plt
import matplotlib.animation as manimation


def maprf(datapath, logpath, staflag):
    sweeptiming = loadsweeptimes(datapath)
    numberofshanks = 8
    (spiketimes, cellnumber) = loadclu(datapath, numberofshanks)
    (sweeporder, sweeptable, bgdimnames) = getSweepTimesEP(logpath)
    #yi = sweeptable[0]
    #xi = sweeptable[1]
    #brightness = sweeptable[8]
    col = sweeptable[0][bgdimnames.index('Color')]
    xi = sweeptable[0][bgdimnames.index('PosX')]
    yi = sweeptable[0][bgdimnames.index('PosY')]
    
    '''count spikes per sweep'''
    firstspike = findlevel(spiketiming, sweeptiming[0])
    spikecount = np.zeros((len(sweeptiming),1))
    for i in range(0,(len(sweeptiming)-1)):
        sweepstart = sweeptiming[i]
        sweepend = sweeptiming[(i+1)]
        for j in range(firstspike, (firstspike+100)):
            if spiketiming[j] >= sweepstart and spiketiming[j] < sweepend:
                spikecount[i] += 1
                tempj = j
        firstspike = tempj
        spikecount[i] /= (sweepend - sweepstart)
    spikecount *= 20000 
    
    '''arranges stimulus conditions'''    
    stimuluscondition = np.zeros((len(sweeporder),4))
    for i in range(0, len(sweeporder)):    
        j = sweeporder[i]        
#        stimuluscondition[i,0] = brightness[j]
#        stimuluscondition[i,1] = xi[j]
#        stimuluscondition[i,2] = yi[j]
#        stimuluscondition[i,3] = spikecount[i]
        stimuluscondition[i,0] = sweeptable[i][col]
        stimuluscondition[i,1] = sweeptable[i][xi]
        stimuluscondition[i,2] = sweeptable[i][yi]
        stimuluscondition[i,3] = spikecount[i]
    
    nxp = ((amax(stimuluscondition[:,1])-amin(stimuluscondition[:,1]))/5)+1
    nyp = ((amax(stimuluscondition[:,2])-amin(stimuluscondition[:,2]))/5)+1
    
    if staflag == 0:
        '''on and off count maps'''
        onrf = np.zeros((nxp,nyp))
        offrf = np.zeros((nxp,nyp))
        oncount = np.zeros((nxp,nyp))
        offcount = np.zeros((nxp,nyp))
    
        for i in range(0,len(stimuluscondition)):
            if stimuluscondition[i,0] == 0:
                offrf[stimuluscondition[i,1],stimuluscondition[i,2]] += stimuluscondition[i,3]            
                offcount[stimuluscondition[i,1],stimuluscondition[i,2]] += 1
            if stimuluscondition[i,0] == 1:
                onrf[stimuluscondition[i,1],stimuluscondition[i,2]] += stimuluscondition[i,3]            
                oncount[stimuluscondition[i,1],stimuluscondition[i,2]] += 1
        offrf /= offcount
        onrf /= oncount
        rf = np.zeros((16,16))
        rf = (onrf - offrf)/(onrf + offrf)
        imshow(rf, cmap="RdBu", vmin=-1, vmax=1)
        xlabel("X position", fontsize=20)
        ylabel("Y position", fontsize=20)
        tick_params(labelsize=20)
        cbar = colorbar()
        cbar.ax.set_ylabel('(ON-OFF)/(ON+OFF)', fontsize=16)         
        show()
        return rf
        
    if staflag == 1:
        '''simple spike triggered average (downsampled to 1 kHz)'''
        '''make stimulus movie'''
        stimmovie = np.zeros((16,16,len(sweeptiming)*133))
        stimmovie += 0.5
        adjust = sweeptiming[0]
        sweepadjust = (sweeptiming - adjust)/20
        spikeadjust = (spiketiming - adjust)/20
        for i in range(0,len(stimuluscondition)):
            smx = stimuluscondition[i,1]
            smy = stimuluscondition[i,2]
            smst = sweepadjust[i]
            smend = sweepadjust[i+1]
            stimmovie[smx,smy,smst:smend] = stimuluscondition[i,0]
        
        '''do STA'''
        rfstatop = np.zeros((16,16,1000))
        '''rfstabottom = np.zeros((16,16,1000))'''
        rfstabottom = np.zeros((size(stimmovie,2),1))
        rfsta = np.zeros((16,16,1000))
        firstspike = findlevel(spikeadjust,1000)
        lastspike = findlevel(spikeadjust,size(stimmovie,2)) - 1
        for i in range(firstspike, lastspike):
            j = spikeadjust[i]
            rfstatop[:,:,] += stimmovie[:,:,j-1000:j]
        rfstatop/=(lastspike - firstspike)
        
        '''for i in range(1000,size(stimmovie,2)):
            #rfstabottom[:,:,:] += stimmovie[:,:,i-1000:i]
            rfstabottom[:] += stimmovie[7,7,i-1000:i]
        rfstabottom/=(size(stimmovie,2)-1000)'''
        #rfstabottom = stimmovie[7,7,0:999]        
        #rfstabottom = np.cov(stimmovie.T)
        
        rfsta = rfstatop
        #/rfstabottom
        
        #make movie        
        import os, sys
        import matplotlib.pyplot as plt
 
        for i in range(1000):
            plotRF(rfsta, i)
            fname = '_tmp%05d.png'%i
            plt.savefig(fname)
            plt.clf()
 
        try: 
            os.system("del movie.avi")
        except:
            print "movie.mpg not found, a new one will be created."

        os.system("ffmpeg -f image2 -i _tmp%05d.png movie.avi")
        os.system("del _tmp*.png")
        
        
        return rfsta
                      



def plotRF(RF, frame):
    rfi = RF[:,:,frame]        
    imshow(rfi, cmap="RdBu", vmin=0.498, vmax=0.502)
    colorbar()
    
    
    
datapath = "C:\Users\saskiad\Documents\ephys\20130228_M10_Sparse2\20130228_M10_Sparse2"
logpath = r"C:\Users\saskiad\Documents\ephys\SPARSE2\130228143420-M9.log"

rf = maprf(datapath, logpath, 0)