# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 09:45:01 2013

@author: saskiad
"""
import numpy as np
from pylab import *

def findlevelbuffer(inwave, threshold, endbuffer):
    inwave = insert(inwave,0,0)
    inwave = append(inwave,endbuffer)
    temp = findlevel(inwave, threshold)
    return (temp-1)
#    for i in range(1,(size(inwave))):
#        if (inwave[i]) >= threshold and (inwave[(i-1)]) < threshold:            
#            return i-1
    

def findlevel(inwave, threshold, direction='both'):
    temp = inwave - threshold
    if (direction.find("up")+1):
        crossings = np.nonzero(np.ediff1d(np.sign(temp), to_begin=0)>0)
    elif (direction.find("down")+1):
        crossings = np.nonzero(np.ediff1d(np.sign(temp), to_begin=0)<0)
    else:
        crossings = np.nonzero(np.ediff1d(np.sign(temp), to_begin=0))
    return crossings[0][0]
    
    
def findlevels(inwave, threshold, window, direction='both'):
    duplicates = []
    temp = inwave - threshold

    if (direction.find("up")+1):
        crossings = np.nonzero(np.ediff1d(np.sign(temp), to_begin=0)>0)
        zdiff = np.ediff1d(crossings, to_begin=(window*2))
        for i in range(size(zdiff)):
            if zdiff[i] < window:
                duplicates.append(i)
        levels = np.delete(crossings, duplicates)        
    elif (direction.find("down")+1):
        crossings = np.nonzero(np.ediff1d(np.sign(temp), to_begin=0)<0)
        zdiff = np.ediff1d(crossings, to_begin=(window*2))
        for i in range(size(zdiff)):
            if zdiff[i] < window:
                duplicates.append(i)
        levels = np.delete(crossings, duplicates)
    else:
        crossings = np.nonzero(np.ediff1d(np.sign(temp), to_begin=0))
        zdiff = np.ediff1d(crossings, to_begin=(window*2))
        for i in range(size(zdiff)):
            if zdiff[i] < window:
                duplicates.append(i)
        levels = np.delete(crossings, duplicates)
    
    return levels
            
            
            
def findlevelsold(inwave, threshold, window):
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
       
def findlevelsolddown(inwave, threshold, window):
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

def findlevelold(inwave, threshold):
    '''script to find a single upward threshold crossing'''
    for i in range(0,(size(inwave))):
        if np.logical_and(((inwave[i]) >= threshold),((inwave[(i-1)]) < threshold)):            
            return i

def findlevelolddown(inwave, threshold):
    '''script to find a single downward threshold crossing'''
    for i in range(0,(size(inwave)-1)):
        if inwave[i] <= threshold and inwave[(i-1)] > threshold:
            return i