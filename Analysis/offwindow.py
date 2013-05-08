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


def offwindow(logpath):
    f = open(logpath, 'r')
    exec(f.read())
    f.close()
    
    '''monitor and stimulus properties'''
    monitorpix = monitor['sizepix'][0]
    objectsize = terrain['objectwidthDeg']
    monitordeg = 2*(math.degrees(math.atan((monitor['widthcm'] / 2) / monitor['distancecm'])))
    pixperdeg = monitorpix / monitordeg
    
    on = np.empty((len(laps),1))    
    for i in range(len(laps)):
        on[i] = laps[i][1]
        
    offthr = (monitorpix / 2) + (objectsize * pixperdeg / 2)        
    posxt = array(posx)     
    off = findlevels(posxt, offthr, 10, 'up')
    
    for i in range(len(laps)):
        if off[i] - on[i-1] < 10:
            off = np.delete(off,i)
    
    on = np.insert(on, 0, 0)
    
    if len(on) == len(off):
        print "Okay to Go!"
    else:
        sys.exit('Problems with posx')
    
    return (on, off)
    

if __name__=='__main__':
    logpath = r'C:\Users\saskiad\Documents\130422221446-CA211_130422_AleenaOri_-50_20_task.log'
    (on, off) = offwindow(logpath)

