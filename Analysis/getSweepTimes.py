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
    ori = bgsweeptable [0][bgdimnames.index('Ori')]
    con = bgsweeptable[0][bgdimnames.index('Contrast')]
    xp = bgdimnames.index('PosX')
    yp = bgdimnames.index('PosY')
    
    if (modality.find("sf")+1):
        sortcondition = bgdimnames.index('SF')
        tlabel = "Spatial frequency (Cyc/Deg)"
        print tlabel
    elif (modality.find("tf")+1):
        sortcondition = bgdimnames.index('TF')
        tlabel = "Temporal frequency (Cyc/Sec)"
        print tlabel
    elif (modality.find("ori")+1):
        sortcondition = bgdimnames.index('Ori')
        tlabel = "Orientation (Deg)"
        print tlabel
    elif (modality.find("conrev")+1):
        sortcondition = bgdimnames.index('Phase')
        tlabel =  "Phase"
        print tlabel
    else:
        print "No modality specified"
    
    stimuluscondition = np.zeros((len(bgsweeporder),5))    
    for i in range(len(bgsweeporder)):
        #sweep start        
        stimuluscondition[i,0] = (preexpsec + (i*sweeplength) + (i*postsweepsec))
        #sweep end        
        stimuluscondition[i,1] = (preexpsec + (i*sweeplength) + (i*postsweepsec) + sweeplength)
        #sweep conditions (xp, yp, ori)
        si = bgsweeporder[i]
        if si >= 0:
            stimuluscondition[i,2] = bgsweeptable[si][xp]
            stimuluscondition[i,3] = bgsweeptable[si][yp]
            stimuluscondition[i,4] = bgsweeptable[si][sortcondition]
    
    if postsweepsec > 0:
        for i in range(1, len(stimuluscondition), 2):
            tin = array([(stimuluscondition[i-1,1]+1), stimuluscondition([i+1,0]-1), stimuluscondition[i-1,2], stimuluscondition[i-1,3], NaN])
            stimuluscondition = insert(stimuluscondition, i, tin, 0)
    
    '''sorts on xp, yp, sortcondition'''     
    stimuluscondition = stimuluscondition[np.lexsort((stimuluscondition[:,4], stimuluscondition[:,3], stimuluscondition[:,2]))]

    return (stimuluscondition, sweeplength)

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
    ori = bgsweeptable [0][bgdimnames.index('Ori')]
    con = bgsweeptable[0][bgdimnames.index('Contrast')]
    
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
#    elif (modality.find("conrev")+1):
#        sortcondition = bgdimnames.index('Phase')
#        constring = str(spfreq)+' Cyc/Deg'
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
            stimuluscondition[i,1] = NaN
            stimuluscondition[i,2] = NaN
            stimuluscondition[i,3] = bgsweeptable[(bgsweeporder[i-1])][bgdimnames.index('TF')]
    
    '''sort sweep times by orientation, spatial frequency, temporal frequency'''
    #stimuluscondition = stimuluscondition[stimuluscondition[:,0].argsort()]
    stimuluscondition = stimuluscondition[np.lexsort((stimuluscondition[:,3], stimuluscondition[:,2], stimuluscondition[:,1]))]
    
    return (stimuluscondition, duration, constring)
    #return (bgsweeporder, bgsweeptable, bgdimnames)


if __name__ == '__main__':
    #logpath = r'I:\CA153_130307\130307124929-CA153_130307_b.log'
    #(stimuluscondition, sweeplength) = getSweepTimesOP(logpath, 'ori')
    
    logpath = r'C:\Users\saskiad\Documents\ephys\ORI4\130228134828-M10.log'
    datapath = r"C:\Users\saskiad\Documents\ephys\20130228_M10_Ori4\20130228_M10_Ori4"
    (stimuluscondition, duration, constring) = getSweepTimesEP(logpath, datapath, 'ori')
