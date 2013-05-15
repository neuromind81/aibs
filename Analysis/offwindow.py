# -*- coding: utf-8 -*-
"""
Created on Tue May 07 16:45:31 2013

@author: saskiad
"""

from pylab import *
import scipy as sp
import numpy as np
from findlevel import *
import math
import sys


def offstim(logpath, modality):
    '''segregates stimuluscondition into offstim (when fg object off monitor) and on stim (when fg object on monitor)'''
    offon = offwindow(logpath)
    (stimuluscondition, sweeplength, constring) = getSweepTimesOP(logpath, modality)

    stimoff = []
    stimon = []
    for i in range(len(stimuluscondition)):
        sweepst = stimuluscondition[i,0]
        sweepend = stimuluscondition[i,1]
        startp = findlevel(offon[:,0], sweepst, 'up') - 1
        if sweepst < offon[startp,1]:
            '''start of sweep when OFF'''
            if sweepend < offon[startp,1]:
                tin = array(sweepst, sweepend, stimuluscondition[i,2], stimuluscondition[i,3], stimuluscondition[i,4], stimuluscondition[i,5], stimuluscondition[i,6])
            if sweepend > offon[startp,1]:
                tin = array(sweepst, offon[startp,1], stimuluscondition[i,2], stimuluscondition[i,3], stimuluscondition[i,4], stimuluscondition[i,5], stimuluscondition[i,6])
                

            stimoff = append(stimuluscondition, i, tin, 0)
            
            
        else:
            '''start of sweep when ON'''



def offwindow(logpath):
    '''finds when fg object is on or off the monitor'''
    f = open(logpath, 'r')
    exec(f.read())
    f.close()
    
    '''monitor and stimulus properties'''
    monitorpix = monitor['sizepix'][0]
    objectsize = terrain['objectwidthDeg']
    monitordeg = 2*(math.degrees(math.atan((monitor['widthcm'] / 2) / monitor['distancecm'])))
    pixperdeg = monitorpix / monitordeg
    
    '''when object is on the monitor'''
    on = np.empty((len(laps),1))    
    for i in range(len(laps)):
        on[i] = laps[i][1]
    
    '''when object is off the monitor'''    
    offthr = (monitorpix / 2) + (objectsize * pixperdeg / 2)        
    posxt = array(posx)     
    off = findlevels(posxt, offthr, 10, 'up')
    
    '''fixes little weird moments'''
    for i in range(1, len(laps)):
        if off[i] - on[i-1] < 10:
            off = np.delete(off,i)
    
    #on = np.insert(on, 0, 0)
    
    if len(on) == len(off):
        print "Okay to Go!"
        offon = off
        offon = np.column_stack((offon, on))
    else:
        if posxt[len(posxt)-1] < offthr:
            np.append(off, posxt[len(posxt)-1])
        else:   
            on = append(on, NaN)
        offon = off
        offon = np.column_stack((offon, on))
        #sys.exit('Problems with posx')
    return offon
   

if __name__=='__main__':
    logpath = r'C:\Users\saskiad\Documents\130422221446-CA211_130422_AleenaOri_-50_20_task.log'
    offon = offwindow(logpath)

