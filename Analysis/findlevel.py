# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 09:45:01 2013

@author: saskiad
"""
import numpy as np
from pylab import *

def findlevel(inwave, threshold):
    '''script to find a single upward threshold crossing'''
    for i in range(0,(size(inwave)-1)):
        if (inwave[i]) >= threshold and (inwave[(i-1)]) < threshold:            
            return i

def findlevelbuffer(inwave, threshold, endbuffer):
    inwave = insert(inwave,0,0)
    inwave = append(inwave,endbuffer)
    for i in range(1,(size(inwave))):
        if (inwave[i]) >= threshold and (inwave[(i-1)]) < threshold:            
            return i-1
    

def findleveldown(inwave, threshold):
    '''script to find a single downward threshold crossing'''
    for i in range(0,(size(inwave)-1)):
        if inwave[i] <= threshold and inwave[(i-1)] > threshold:
            return i

def findlevels(inwave, threshold, window):
    '''script to find a multiple threshold crossing'''
    '''as written, window in points, not time'''
    levels = []
    i = 1
    while i < size(inwave):
        if (inwave[i]) >= threshold and (inwave[(i-1)]) < threshold:            
            levels.append(i)
            i += window
        else:
            i += 1
    return levels
    
def findlevelsdown(inwave, threshold, window):
    '''script to find a multiple downward threshold crossing'''
    '''as written, window in points, not time'''
    levels = []
    i = 1
    while i < size(inwave):
        if (inwave[i]) <= threshold and (inwave[(i-1)]) > threshold:            
            levels.append(i)
            i += window
        else:
            i += 1
    return levels