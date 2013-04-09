# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 16:00:28 2013

@author: saskiad
"""

from pylab import *
import scipy as sp
#import scipy.io as sio
import numpy as np
#from loadlog import *
from getSweepTimes import *
from loadclu import *
from scipy.optimize import curve_fit
from multipsth import *
from findlevel import *
import matplotlib.pyplot as plt

'''***important***
must indicate which modality is being varied in the given data set, using following code:
    sf = spatial frequency
    tf = temporal frequency
    sftf = spatial and temporal frequency combined
    ori = orientation
    
'''

def flashgrating (datapath, logpath, modality, numbins, showflag):
    print "loading data from:",datapath
    numberofshanks = 8
    '''get data'''    
    #sweeptiming = loadsweeptimes(datapath)
    (spiketimes, cellnumber) = loadclu(datapath, numberofshanks)
    nc = size(spiketimes,1)
    
    '''get log'''
    #(sweeporder, sweeptable, bgdimnames) = getSweepTimesEP(logpath)
    (stimc, duration, constring) = getSweepTimesEP(logpath, datapath, modality)    
    
    tfreq = stimc[0,3]  
    
    if (modality.find("sf")+1):
        tlabel = "Spatial frequency (Cyc/Deg)"
        ticks = range(0, 0.6, 0.05)
        print tlabel
        print constring
        orivals = np.unique(stim[:,1])
        for i in range(len(orivals)):
            stimuluscondition = stimc[np.where(stimc[:,1] == orival[i])]
            ostr = str(orival[i])+"Deg"            
            constring = constring + " at " + ostr 
            dotuning(stimuluscondition, spiketimes, cellnumber, 2, tlabel, ticks, constring, ostr, numbins, showflag)                
    elif (modality.find("tf")+1):
        tlabel = "Temporal frequency (Cyc/Sec)"
        ticks = range(0,15,3)
        print tlabel
        print constring
        orivals = np.unique(stim[:,1])
        for i in range(len(orivals)):
            ostr = str(orival[i])+"Deg"
            constring = constring + " at " + ostr
            stimuluscondition = stimc[np.where(stimc[:,1] == orival[i])]
            dotuning(stimuluscondition, spiketimes, cellnumber, 3, duration, tlabel, ticks, constring, ostr, numbins, showflag)
    elif (modality.find("ori")+1):
        tlabel = "Orientation (Deg)"
        ticks = range(0,360,45)
        print tlabel
        print constring
        stimuluscondition = stimc
        ostr = "allori"
        dotuning(stimuluscondition, spiketimes, cellnumber, 1, duration, tlabel, ticks, constring, ostr, numbins, showflag)
    else:
        print "No modality specified"
    
    fileout = datapath+'_cellnumber.dat'    
    np.savetxt(fileout, cellnumber,'%f')
        
#    if modality.find('ori')<0:
#        orivals = np.unique(stim[:,1])
#        for i in range(len(orivals)):
#            stimuluscondition = stimc[np.where(stimc[:,1] == orival[i])]
#            dotuning(stimuluscondition, spiketimes, cellnumber, tlabel, ticks, numbins, showflag)
#    else:
#        stimuluscondition = stimc
#        dotuning(stimuluscondition, spiketimes, cellnumber, 1, tlabel, ticks, numbins, showflag)
    
    
    
    '''make different script below'''
    
def dotuning(stimuluscondition, spiketimes, cellnumber, sortc, duration, tlabel, ticks, constring, ostr, numbins, showflag):
    nc = size(spiketimes,1)
    
    '''sort sweep times by sort condition'''
    #stimuluscondition = stimuluscondition[stimuluscondition[:,1].argsort()]
    
    valuedifference = np.ediff1d(stimuluscondition[:,sortc], to_end=None, to_begin = 1)
    '''difference between values'''
    transitions = argwhere(valuedifference)    
    '''indices for condition transitions'''
        
    transitions = append(transitions, len(valuedifference))
    
    f0 = np.zeros((len(stimuluscondition),nc))    
    f1 = np.zeros((len(stimuluscondition),nc))
    f2 = np.zeros((len(stimuluscondition),nc))
    for sweep in range(0,len(stimuluscondition)):
#        if (modality.find("tf")+1):
#            tfreq = stimuluscondition[sweep,3]
        tfreq = stimuluscondition[sweep,3]       
        starttimes = np.zeros((tfreq*duration,1))
        for cj in range(0,len(starttimes)):        
            starttimes[cj] = stimuluscondition[sweep,0] + (cj/tfreq)
        binsize = (1/tfreq)/numbins
        spikepsth = multipsth(spiketimes, starttimes, (1/tfreq), numbins, showflag)
        '''makes psth for each cell per sweep'''
        temp1 = delete(spikepsth,0,1)
        #deletes the bintimes, just the psths remain
        fourier = abs(np.fft.fft(temp1,axis=0))
        freq = np.fft.fftfreq(len(temp1), d=binsize)
        '''fourier analysis'''
        f0[sweep,:] = mean(temp1, axis=0)
        f1[sweep,:] = fourier[argwhere(freq == tfreq)]
        f2[sweep,:] = fourier[argwhere(freq == (2*tfreq))]
        #what are the units that the fft returns?
    
    f0mean = np.zeros(((len(transitions)-1),nc))
    f0sem = np.zeros(((len(transitions)-1),nc))
    f1mean = np.zeros(((len(transitions)-1),nc))
    f1sem = np.zeros(((len(transitions)-1),nc))
    f2mean = np.zeros(((len(transitions)-1),nc))
    f2sem = np.zeros(((len(transitions)-1),nc))
    tuning = np.zeros(((len(transitions)-1),1))
    for t in range(len(tuning)):
        tuning[t] = stimuluscondition[transitions[t],sortc]    
    for cond in range(len(tuning)):
        firstpoint = transitions[cond]
        lastpoint = transitions[cond+1]
        temp = f0[firstpoint:lastpoint,:]
        f0mean[cond,:] = temp.mean(0)
        f0sem[cond,:] = temp.std(0)/sqrt(lastpoint-firstpoint)        
        temp = f1[firstpoint:lastpoint,:]
        f1mean[cond,:] = temp.mean(0)
        f1sem[cond,:] = temp.std(0)/sqrt(lastpoint-firstpoint)
        temp = f2[firstpoint:lastpoint,:]
        f2mean[cond,:] = temp.mean(0)
        f2sem[cond,:] = temp.std(0)/sqrt(lastpoint-firstpoint)
    '''averages same stim condition measurements together'''
        
#    for s in range(1,numberofshanks+1):
    for s in range(1,9):
        firstcell = findlevelbuffer(cellnumber, s, 100) 
        lastcell = findlevelbuffer(cellnumber, (s+1), 100) - 1
        if lastcell > firstcell:     
            sn = lastcell - firstcell + 1
            print "shank #"+str(s)+" has "+str(sn)+" cells"
            figure(s)        
            for c in range(sn):
                sp = c + firstcell
                subplot(ceil(sqrt(sn)), round(sqrt(sn)), c+1)
                errorbar(tuning, f1mean[:,sp], yerr=f1sem[:,sp], fmt = 'ro', capsize=2, linestyle='-')
                errorbar(tuning, f0mean[:,sp], yerr=f0sem[:,sp], fmt = 'bx', capsize=2, linestyle='-')
                if (modality.find("conrev")+1):
                    errorbar(tuning, f2mean[:,sp], yerr=f2sem[:,sp], fmt = 'go', capsize=2, linestyle='-')
                xticks(ticks)             
                xlabel(tlabel, fontsize=10)
                ylabel("(spk/s)", fontsize=10)
                text(1,1, str(c+1), fontsize=10)
                tick_params(axis='both', which='major', labelsize=7)
            suptitle("Shank #"+str(s)+':'+constring, fontsize=14)
            legend(('f1','mean'),loc=4, prop={'size':10}) 
            fname = datapath+'_'+ostr+'_tuning'+str(s)+'.png'
            savefig(fname)
            show()
    
    '''save data'''    
    fileout = datapath+'_'+ostr+'_tuning.dat'    
    np.savetxt(fileout, tuning,'%f')
    fileout = datapath+'_'+ostr+'_F0mean.dat'    
    np.savetxt(fileout, f0mean,'%f')
    fileout = datapath+'_'+ostr+'_F0sem.dat'    
    np.savetxt(fileout, f0sem,'%f')
    fileout = datapath+'_'+ostr+'_F1mean.dat'    
    np.savetxt(fileout, f1mean,'%f')
    fileout = datapath+'_'+ostr+'_F1sem.dat'    
    np.savetxt(fileout, f1sem,'%f')
    fileout = datapath+'_'+ostr+'_F1mean.dat'    
    np.savetxt(fileout, f1mean,'%f')
    fileout = datapath+'_'+ostr+'_F2mean.dat'    
    np.savetxt(fileout, f2mean,'%f')
    fileout = datapath+'_'+ostr+'_F1mean.dat'    
    np.savetxt(fileout, f1mean,'%f')
    fileout = datapath+'_'+ostr+'_F2sem.dat'    
    np.savetxt(fileout, f2sem,'%f')
    
    return (cellnumber, tuning, f0mean, f0sem, f1mean, f1sem, f2mean, f2sem)
    #np.savetxt(fileout,A,'%f')    


if __name__ == '__main__':
    datapath = r"C:\Users\saskiad\Documents\ephys\20130228_M10_Ori4\20130228_M10_Ori4"
    logpath = r"C:\Users\saskiad\Documents\ephys\ORI4\130228134828-M10.log"
    numbins = 64.0
    showflag = 0
    modality = 'ori'
    #binsize as 128 bins per stimulus cycle?
    (cellnumber, tuning, f0mean, f0sem, f1mean, f1sem, f2mean, f2sem) = flashgrating (datapath, logpath, modality, numbins, showflag)


