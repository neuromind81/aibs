# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 17:00:31 2013

@author: saskiad
"""
from pylab import nan
import numpy as np
from loadlog import *

def getSweepTimesOP(path, modality):
    '''uses .log file to get stimulus sweep timing and stimulus conditions'''
    f = open(path, 'r')
    exec(f.read())
    
    '''sweep parameters in number of frames'''
    sweeplength = 60 * genericparams['sweeplength']
    preexpsec = 60 * genericparams['preexpsec']
    postexpsec = 60 * genericparams['postexpsec']
    postsweepsec = 60 * genericparams['postsweepsec']
    
    spfreq = float(bgsweeptable[0][bgdimnames.index('SF')])
    tfreq = float(bgsweeptable[0][bgdimnames.index('TF')])    
    
    if (modality.find("sf")+1):
        constring = str(tfreq)+' Cyc/Sec'
    elif (modality.find("tf")+1):
        constring = str(spfreq)+' Cyc/Deg'
    elif (modality.find("ori")+1):
        constring= str(tfreq)+' Cyc/Sec and '+str(spfreq)+' Cyc/Deg'
    else:
        print "No modality specified"
    
    '''makes stimuluscondition table'''
    '''sweep start, sweep end, xpos, ypos, ori, sf, tf'''    
    stimuluscondition = np.zeros((len(bgsweeporder),7))    
    for i in range(len(bgsweeporder)):       
        stimuluscondition[i,0] = int(preexpsec + (i*sweeplength) + (i*postsweepsec))     
        stimuluscondition[i,1] = int(preexpsec + (i*sweeplength) + (i*postsweepsec) + sweeplength)
        si = bgsweeporder[i]
        if si >= 0:
            stimuluscondition[i,2] = bgsweeptable[si][bgdimnames.index('PosX')]
            stimuluscondition[i,3] = bgsweeptable[si][bgdimnames.index('PosY')]
            stimuluscondition[i,4] = bgsweeptable[si][bgdimnames.index('Ori')]
            stimuluscondition[i,5] = bgsweeptable[si][bgdimnames.index('SF')]
            stimuluscondition[i,6] = bgsweeptable[si][bgdimnames.index('TF')]
    '''inter-sweep intervals''' 
    if postsweepsec > 0:
        for i in range(1, len(stimuluscondition)*2-1, 2):
            tin = array([stimuluscondition[(i-1),1]+1, stimuluscondition[i,0]-1, stimuluscondition[(i-1),2], stimuluscondition[(i-1),3], stimuluscondition[(i-1),4]+1, 1111, 1111])
            stimuluscondition = insert(stimuluscondition, i, tin, 0)
    
    '''sorts on xp, yp, ori, sf, tf'''     
    stimuluscondition = stimuluscondition[np.lexsort((stimuluscondition[:,6], stimuluscondition[:,5], stimuluscondition[:,4], stimuluscondition[:,3], stimuluscondition[:,2]))]
    return (stimuluscondition, sweeplength, constring)

def getSweepTimesEP(logpath, datapath, modality):
    sweeptiming = loadsweeptimes(datapath)
    duration = round(sweeptiming[0,1]-sweeptiming[0,0])
    
    print "Getting sweep info from:",logpath
    f = open(logpath, 'r')
    exec(f.read())
    f.close()
    
    '''relevant parameters'''  
    spfreq = float(bgsweeptable[0][bgdimnames.index('SF')])
    tfreq = float(bgsweeptable[0][bgdimnames.index('TF')])    
#    ori = bgsweeptable [0][bgdimnames.index('Ori')]
#    con = bgsweeptable[0][bgdimnames.index('Contrast')]
    
    if (modality.find("sf")+1):
        sortcondition = 2
        constring = str(tfreq)+' Cyc/Sec'
    elif (modality.find("tf")+1):
        sortcondition = 3
        constring = str(spfreq)+' Cyc/Deg'
    elif (modality.find("ori")+1):
        sortcondition = 1
        constring= str(tfreq)+' Cyc/Sec and '+str(spfreq)+' Cyc/Deg'
    elif (modality.find("sftf")+1):
        constring = ''
    else:
        print "No modality specified"
    
    stimuluscondition = np.zeros((len(sweeptiming),4))
    for i in range(0, len(sweeptiming)):    
        j = bgsweeporder[i]
        if j >= 0:
            stimuluscondition[i,0] = sweeptiming[i,0]            
            stimuluscondition[i,1] = bgsweeptable[j][bgdimnames.index('Ori')]
            stimuluscondition[i,2] = bgsweeptable[j][bgdimnames.index('SF')]
            stimuluscondition[i,3] = bgsweeptable[j][bgdimnames.index('TF')]            
        elif j < 0:
            stimuluscondition[i,0] = sweeptiming[i,0]            
            stimuluscondition[i,1] = 1111
            stimuluscondition[i,2] = 1111
            stimuluscondition[i,3] = bgsweeptable[(bgsweeporder[i-1])][bgdimnames.index('TF')]
    
    '''sort sweep times by orientation, spatial frequency, temporal frequency'''
    #stimuluscondition = stimuluscondition[stimuluscondition[:,0].argsort()]
    stimuluscondition = stimuluscondition[np.lexsort((stimuluscondition[:,3], stimuluscondition[:,2], stimuluscondition[:,1]))]
    
    return (stimuluscondition, duration, constring)
    #return (bgsweeporder, bgsweeptable, bgdimnames)
    
def getSweepTimesEPrf(path):
    print "Getting sweep info from:",path
    f = open(path, 'r')
    exec(f.read())
    f.close()
    
    '''sweep parameters in number of frames'''
    sweeplength = genericparams['sweeplength']
    preexpsec = genericparams['preexpsec']
    postexpsec = genericparams['postexpsec']
    postsweepsec = genericparams['postsweepsec']
    
    stimtiming = np.zeros((len(bgsweeporder),2))    
    for i in range(len(bgsweeporder)):
        #sweep start        
        stimtiming[i,0] = ((i*sweeplength) + (i*postsweepsec))
        #sweep end        
        stimtiming[i,1] = ((i*sweeplength) + (i*postsweepsec) + sweeplength)
    
    
    return (bgsweeporder, bgsweeptable, bgdimnames, stimtiming)


if __name__ == '__main__':
#    logpath = r'Z:\ImageData\CA211_130331_OriAleena_pos_-50_20b\130331135955-CA211_130331_OriAleena_pos_-50_20b.log'
#    (stimuluscondition, sweeplength) = getSweepTimesOP(logpath, 'ori')
    
#    logpath = r'C:\Users\saskiad\Documents\ephys\ORI4\130228134828-M10.log'
#    datapath = r"C:\Users\saskiad\Documents\ephys\20130228_M10_Ori4\20130228_M10_Ori4"
#    (stimuluscondition, duration, constring) = getSweepTimesEP(logpath, datapath, 'ori')

    path = r"E:\CLUtoANALYZE25mars2013\M14logs\SPARSE1\130314145849-M14.log"
    (bgsweeporder, bgsweeptable, bgdimnames, stimtiming) = getSweepTimesEPrf(path)
