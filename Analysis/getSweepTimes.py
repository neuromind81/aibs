# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 17:00:31 2013

@author: saskiad
"""
from pylab import nan
import numpy as np

def getSweepTimesOP(path):
    '''uses .log file to get stimulus sweep timing and stimulus conditions'''
    f = open(path, 'r')
    exec(f.read())
    
    '''sweep parameters in number of frames'''
    sweeplength = 60 * genericparams['sweeplength']
    preexpsec = 60 * genericparams['preexpsec']
    postexpsec = 60 * genericparams['postexpsec']
    postsweepsec = 60 * genericparams['postsweepsec']
    
    stimuluscondition = np.zeros((len(bgsweeporder),5))    
    for i in range(len(bgsweeporder)):
        #sweep start        
        stimuluscondition[i,0] = (preexpsec + (i*sweeplength) + (i*postsweepsec))
        #sweep end        
        stimuluscondition[i,1] = (preexpsec + (i*sweeplength) + (i*postsweepsec) + sweeplength)
        #sweep conditions (xp, yp, ori)
        si = bgsweeporder[i]
        if si >= 0:
            stimuluscondition[i,2] = bgsweeptable[si][4]
            stimuluscondition[i,3] = bgsweeptable[si][5]
            stimuluscondition[i,4] = bgsweeptable[si][1]
            
    return stimuluscondition

def getSweepTimesEP(path):
    print "Getting sweep info from:",path
    f = open(path, 'r')
    exec(f.read())
    f.close()
    
    return (bgsweeporder, bgsweeptable, bgdimnames)


if __name__ == '__main__':
    logpath = r"C:\Users\saskiad\Documents\ephys\ORI4\130228134828-M10.log"
    (sweeporder, sweeptable, bgdimnames) = getSweepTimesEP(logpath)
