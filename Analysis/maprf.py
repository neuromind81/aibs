# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 15:15:32 2013

@author: saskiad
"""
import h5py
import matplotlib
from pylab import *
import scipy as sp
import numpy as np
from loadlog import *
from loadclu import loadclu
from getSweepTimes import *
from findlevel import findlevel
import matplotlib.pyplot as plt
import matplotlib.animation as manimation


def maprf(datapath, logpath, showflag, staflag):
    '''maps receptive field for EPhys Data'''
    '''inputs: datapath, logpath, showflag (1=show, 0=no), staflag(1=sta, 0=2DHistogram)'''
    print "loading data from:",datapath    
    #sweeptiming = loadsweeptimesnogap(datapath)
    sweeptimes = loadsweeptimesnogap(datapath)
    print "sweeptiming"
    print str(len(sweeptimes))
    numberofshanks = 8
    (spiketimes, cellnumber) = loadclu(datapath, numberofshanks)
    (sweeporder, sweeptable, bgdimnames, sweeptiming) = getSweepTimesEPrf(logpath)
    #sweeptiming in this call to use stimulus frames to set sweeptimes
    sweeptiming += sweeptimes[0,0]
    nc = size(spiketimes,1)
    
    print "sweeporder"
    print str(len(sweeporder))
    
    col = bgdimnames.index('Color')
    xi = bgdimnames.index('PosX')
    yi = bgdimnames.index('PosY')
    
    '''arranges stimulus conditions'''    
    stimuluscondition = np.zeros((len(sweeporder),3))
    for i in range(0, len(sweeporder)):    
        j = sweeporder[i]        
        stimuluscondition[i,0] = sweeptable[j][col]
        stimuluscondition[i,1] = sweeptable[j][xi]
        stimuluscondition[i,2] = sweeptable[j][yi]
    
    '''number of xpositions and ypositions'''
    nxp = ((amax(stimuluscondition[:,1])-amin(stimuluscondition[:,1]))/5)+1
    nyp = ((amax(stimuluscondition[:,2])-amin(stimuluscondition[:,2]))/5)+1
    
    if staflag == 0:
        print "2D Histogram"
        '''on and off count maps'''
        offrf = np.zeros((nxp,nyp,nc))
        offcount = np.zeros((nxp,nyp))
        onrf = np.zeros((nxp,nyp,nc))
        oncount = np.zeros((nxp,nyp))
        
        '''count spikes per sweep'''
        spikecount = np.zeros((len(sweeptiming), nc))
        cellspikes = sort(spiketimes, axis=0)
        for i in range(len(sweeptiming)):
            (spy, spx) = np.where(np.logical_and(cellspikes >= sweeptiming[i,0], cellspikes < sweeptiming[i,1]))
            for sp in range(len(spx)):
                cn = spx[sp]
                spikecount[i,cn] += 1
        
        print "making rf maps"
        for i in range(0,len(sweeptiming)):
            xp = (stimuluscondition[i,1]-amin(stimuluscondition[:,1]))/5
            yp = (stimuluscondition[i,2]-amin(stimuluscondition[:,2]))/5            
            if stimuluscondition[i,0] == -1:
                offrf[xp,yp,:] += spikecount[i,:]
                offcount[xp,yp] += 1
            elif stimuluscondition[i,0] == 1:
                onrf[xp,yp,:] += spikecount[i,:]
                oncount[xp,yp] += 1
        if amin(offcount) == amax(offcount):
            offrf /= amin(offcount)
        else:
            print "unequal OFF sampling!"
        
        if amin(oncount) == amax(oncount):
            onrf /= amin(oncount)
        else:
            print "unequal ON sampling!"
        #offrf /= offcount
        #onrf /= oncount
        #rf = np.zeros((nxp,nyp,nc))
        #rf = (onrf - offrf)/(onrf + offrf)

        '''plotting?'''
        for s in range(1,numberofshanks+1):
            firstcell = findlevelbuffer(cellnumber, s, 100) 
            lastcell = findlevelbuffer(cellnumber, (s+1), 100) - 1
            if lastcell > firstcell:     
                sn = 2*(lastcell - firstcell + 1)
                print "shank #"+str(s)+" has "+str(sn/2)+" cells"
                figure(s)
                for c in range(sn):
                    sp = c + firstcell
                    ncol = 2 * floor(sqrt(sn/2))
                    nrow = ceil(sn/ncol)
                    subplot(nrow, ncol, c+1)
                    if np.logical_not(mod(c,2)):                    
                        imshow(onrf[:,:,sp/2])
                        title("ON")
                    else:
                        imshow(offrf[:,:,sp/2])
                        title("OFF")
                    #xlabel("X position", fontsize=10)
                    #ylabel("Y position", fontsize=10)
                    xticks([])
                    yticks([])
                    tight_layout()
                    text(0,0, str(int(floor(c/2)+2)), fontsize=10, color='white')
                    #tick_params(labelsize=10)
                    cbar = colorbar()
                    cbar.ax.set_ylabel('(spk/s)', fontsize=8)
                    for t in cbar.ax.get_yticklabels():
                        t.set_fontsize(8)
                subplots_adjust(top=0.9)
                suptitle("Shank #"+str(s), fontsize=14)
                fname = datapath+'_RF'+str(s)+'.png'
                savefig(fname)
                if showflag:
                    show(False)
            
        fullfilename = datapath + '_RFData.h5'
        f = h5py.File(fullfilename)
        dset = f.create_dataset("offRF", offrf.shape, 'f')
        dset[...] = offrf
        dset.attrs["NumberPositions"] = (nxp, nyp)
        dset.attrs["datapath"] = datapath
        dset.attrs["logpath"] = logpath
        dset2 = f.create_dataset("onRF", onrf.shape, 'f')
        dset2[...]=onrf
        f.close()
    
#        fileout = datapath+'_ONRF.dat'    
#        np.savetxt(fileout, onrf,'%f')
#        fileout = datapath+'_OFFRF.dat'    
#        np.savetxt(fileout, offrf,'%f')
        return (onrf, offrf)
        
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
    
    
if __name__ == '__main__':    
    datapath = r"C:\Users\saskiad\Documents\ephys\20130228_M10_Sparse2\20130228_M10_Sparse2"
    logpath = r"C:\Users\saskiad\Documents\ephys\SPARSE2\130228143420-M9.log"
    showflag = 1
    (onrf, offrf) = maprf(datapath, logpath, showflag, 0)
