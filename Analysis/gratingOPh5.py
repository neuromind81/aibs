# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 14:47:49 2013

@author: saskiad
"""


from pylab import *
import scipy as sp
import numpy as np
import os
from loadlog import *
from getSweepTimes import getSweepTimesOP
from OPTools import *


def gratingOP(datapath, logpath, syncpath, savepath, modality, showflag, subX, subY):
    print "loading traces from:", datapath    
    celltraces = loadh5(datapath, 'data_t')
    
    print "loading stimulus log from:",logpath 
    (stimuluscondition, sweeplength, constring) = getSweepTimesOP(logpath, modality)
    print constring
    sweeplength = int((sweeplength/60)*4)
    '''stimuluscondition to synccondition'''
    syncc = getsync(syncpath, stimuluscondition)
    
    temp=[]
    temp = np.where(np.logical_and(syncc[:,2]==subX, syncc[:,3]==subY))
    syncsubtemp = syncc[temp[0][:]]
    temp2 = np.where(np.logical_not(mod(syncsubtemp[:,4],45)))
    syncsub = syncsubtemp[temp2[0][:]]
    
    nc = len(celltraces)
    print "Number of Cells:", nc
    tfreq = 3.0
    
#    if (modality.find("sf")+1):
#        tlabel = "Spatial frequency (Cyc/Deg)"
#        ticks = np.arange(0, 0.62, 0.1)
#        print tlabel
#        #print constring
#        orivals = np.unique(stimc[:,1])
#        orivals = np.delete(orivals, 3, 0)
#        for i in range(len(orivals)):
#            stimuluscondition = stimc[np.where(stimc[:,1] == orivals[i])]
#            ostr = str(orivals[i])+"Deg"            
#            constring = constring + " at " + ostr
#            print ostr
#            (tuning, f0mean, f0sem, f1mean, f1sem, f2mean, f2sem) = dotuning(stimuluscondition, spiketimes, cellnumber, 2, duration, tlabel, ticks, constring, ostr, showflag)                
#    elif (modality.find("tf")+1):
#        tlabel = "Temporal frequency (Cyc/Sec)"
#        ticks = range(0,15,3)
#        print tlabel
#        #print constring
#        orivals = np.unique(stimc[:,1])
#        orivals = np.delete(orivals, 3, 0)
#        for i in range(len(orivals)):
#            ostr = str(orivals[i])+"Deg"
#            constring = constring + " at " + ostr
#            stimuluscondition = stimc[np.where(stimc[:,1] == orivals[i])]
#            print ostr
#            (tuning, f0mean, f0sem, f1mean, f1sem, f2mean, f2sem) = dotuning(stimuluscondition, spiketimes, cellnumber, 3, duration, tlabel, ticks, constring, ostr, showflag)
    if (modality.find("ori")+1):
        tlabel = "Orientation (Deg)"
        ticks = range(0,361,90)
        #print tlabel
        #print constring
        synccondition = syncsub
        ostr = "allori"
        (tuning, f0mean, f0sem) = dotuningOP(syncsub, celltraces, sweeplength, tlabel, ticks, ostr, showflag)
    else:
        print "No modality specified"
        
    newpath = os.path.join(savepath, 'Data')
    if os.path.exists(newpath) == False:
        os.mkdir(newpath)
    
    '''plot data'''
    if showflag:    
        for s in range(int(ceil(nc/9))):
            firstcell = (s*9)
            lastcell = firstcell+8
            figure(s)
            for c in range(9):
                sp = firstcell + c
                if sp<nc:
                    ax1 = subplot(3, 3, c+1)
                    ax1.errorbar(tuning, f0mean[:,sp], yerr=f0sem[:,sp], fmt = 'ro', capsize=2, linestyle='-')
                    ax1.set_ylabel('Mean DF/F', fontsize=10)
                    ax1.set_ylim(bottom=0)
                    xlabel(tlabel, fontsize=10)
                    #if (modality.find("sf")+1) or (modality.find("tf")+1):
                        #ax1.set_xscale('log')
                        #ax2.set_xscale('log')
                    xticks(ticks)             
                    text(0,0, str(sp+1), fontsize=10)
                    tick_params(axis='both', which='major', labelsize=7)
                tight_layout()
            subplots_adjust(top=0.9)
            suptitle(constring + "Cells "+ str(firstcell+1) + " to " + str(lastcell+1), fontsize=14)
            filename = savepath + ostr+'_tuning'+str(s)+'.png'
            fullfilename = os.path.join(newpath, filename) 
            savefig(fullfilename)
            show()
    return (tuning, f0mean, f0sem)
    
    '''save data'''    
#    fileout = matpath+'_'+ostr+'_tuning.dat'    
#    np.savetxt(fileout, tuning,'%f')
#    fileout = matpath+'_'+ostr+'_F0mean.dat'    
#    np.savetxt(fileout, f0mean,'%f')
#    fileout = matpath+'_'+ostr+'_F0sem.dat'    
#    np.savetxt(fileout, f0sem,'%f')
#    fileout = matpath+'_'+ostr+'_F1mean.dat'    
#    np.savetxt(fileout, f1mean,'%f')
#    fileout = matpath+'_'+ostr+'_F1sem.dat'    
#    np.savetxt(fileout, f1sem,'%f')
#    fileout = matpath+'_'+ostr+'_F2mean.dat'    
#    np.savetxt(fileout, f2mean,'%f')
#    fileout = matpath+'_'+ostr+'_F2sem.dat'    
#    np.savetxt(fileout, f2sem,'%f')
        
    
    

def dotuningOP(synccondition, celltraces, sweeplength, tlabel, ticks, ostr, showflag):
    nc = len(celltraces)
    print 'Calculating Tuning'    
    
    '''sort sweep times by sort condition'''
    '''difference between values'''
    valuedifference = np.ediff1d(synccondition[:,4], to_end=None, to_begin = 1)
    '''indices for condition transitions'''
    transitions = argwhere(valuedifference)    
    transitions = append(transitions, len(valuedifference))
    
    #(f0, f1, f2) = gratingfourierOP(celltraces, synccondition, sweeplength, showflag)
    
    f0mean = np.empty(((len(transitions)-1),nc))
    f0sem = np.empty(((len(transitions)-1),nc))
    tuning = np.zeros(((len(transitions)-1),1))
    
    '''mean +- sem for each same stim condition'''
    for t in range(len(tuning)):
        tuning[t] = synccondition[transitions[t],4]    
    for cond in range(len(tuning)):
        firstpoint = transitions[cond]
        lastpoint = transitions[cond+1]
        starttimes = synccondition[firstpoint:lastpoint,0]
        starttimes = starttimes.astype(int32)
        (traceave, tracesem) = OPtraceave(celltraces, starttimes, sweeplength, showflag)     
        f0mean[cond] = traceave.mean(0)
        f0sem[cond] = tracesem.mean(0)
#        temp = f0[firstpoint:lastpoint,:]
#        f0mean[cond,:] = temp.mean(0)
#        f0sem[cond,:] = temp.std(0)/sqrt(lastpoint-firstpoint+1)        
#        temp = f1[firstpoint:lastpoint,:]
#        f1mean[cond,:] = temp.mean(0)
#        f1sem[cond,:] = temp.std(0)/sqrt(lastpoint-firstpoint+1)
#        temp = f2[firstpoint:lastpoint,:]
#        f2mean[cond,:] = temp.mean(0)
#        f2sem[cond,:] = temp.std(0)/sqrt(lastpoint-firstpoint+1)
        
    return (tuning, f0mean, f0sem)
    

def gratingfourierOP(celltraces, synccondition, sweeplength, showflag):
    nc = len(celltraces) 
    f0 = f1 = f2 = np.zeros((len(synccondition),nc))
    for sweep in range(0,len(synccondition)):
        #tfreq = synccondition[sweep,3]
        tfreq = 3.0/4
        starttimes = np.zeros((tfreq*sweeplength,1))
        for cj in range(0,len(starttimes)):        
            starttimes[cj] = synccondition[sweep,0] + (cj/tfreq)
        (traceave, tracesem) = OPtraceave(celltraces, starttimes, sweeplength, showflag)
        fourier = abs(np.fft.fft(traceave,axis=0))
        freq = np.fft.fftfreq(len(traceave), d=binsize)
        '''fourier analysis'''
        f0[sweep,:] = mean(traceave, axis=0)
        f1[sweep,:] = fourier[argwhere(freq == tfreq)]
        f2[sweep,:] = fourier[argwhere(freq == (2*tfreq))]
        return (f0, f1, f2)
        
if __name__=='__main__':
    datapath = r'Z:\ImageData\CA211_130331_OriAleena_pos_-50_20b\CA211_130331_OriAleena_pos_-50_20b_ch2_006_Downsampled\Concat\Traces\Traces_Concat_Downsampled_CA211_130331_OriAleena_pos_-50_20b_ch2_006_f00084.h5'
    logpath = r'Z:\ImageData\CA211_130331_OriAleena_pos_-50_20b\130331135955-CA211_130331_OriAleena_pos_-50_20b.log'
    syncpath = r'Z:\ImageData\CA211_130331_OriAleena_pos_-50_20b\Sync\syncdata.mat'
    savepath = r'Z:\ImageData\CA211_130331_OriAleena_pos_-50_20b\CA211_130331_OriAleena_pos_-50_20b_ch2_006_Downsampled\Concat\Traces'
    modality = 'ori'
    showflag = 1
    subX = -50
    subY = 20
    (tuning, f0mean, f0sem) = gratingOP(datapath, logpath, syncpath, savepath, modality, showflag, subX, subY)