# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 17:00:31 2013

@author: saskiad
"""
from pylab import nan
import numpy as np

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
    #duration = round(sweeptiming[0,1]-sweeptiming[0,0])
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

def getSweepTimesEP(path):
    print "Getting sweep info from:",path
    f = open(path, 'r')
    exec(f.read())
    f.close()
    
    return (bgsweeporder, bgsweeptable, bgdimnames)


if __name__ == '__main__':
    logpath = r'I:\CA153_130307\130307124929-CA153_130307_b.log'
    (stimuluscondition, sweeplength) = getSweepTimesOP(logpath, 'ori')
