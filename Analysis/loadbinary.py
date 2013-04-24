# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 14:06:36 2013

@author: derricw
"""
import numpy as np
from pylab import *

def loadbinary(path, channels = 1, dtype = np.int16):
    f = open(path)
    data = np.fromfile(f,dtype)
    size = len(data)
    del data
    f.close()
    print "Data length:", size
    print "Channels:",channels

    data = np.memmap(path, dtype=dtype,mode='r',shape=((size/channels),channels))
    return data

def loadmeta(path):
    m = open(metapath)
    meta = m.readlines()
    channels = int(meta[7].split(' = ')[1])
    samplerate = int(meta[10].split(' = ')[1])
    
    for item in meta:
        print item.strip()
    return channels, samplerate

if __name__ == "__main__":
    """
    datapath = r"C:\Users\derricw\Documents\data\20130205_test7.dat"
    metapath = r"C:\Users\derricw\Documents\data\20130205_test7.meta"
    """    
    datapath = r"C:\Users\saskiad\Documents\ephys\20130228_M10_Sparse2\20130228_M10_Sparse2.dat"
    metapath = r"C:\Users\saskiad\Documents\ephys\20130228_M10_Sparse2\20130228_M10_Sparse2.meta"
    
       
    channels,_ = loadmeta(metapath)
    data = loadbinary(datapath, channels=channels)

    #Plot a small section of the data.
#    f = figure(0)
#    subset = np.array(data[39.2e6:39.30e6,64:67])
#    plot(subset)
#    xlabel('Sample')
#    ylabel('Voltage')
#    legend(['Sweep','Frame','Diode','Signal'])
#    title('All Channels')
#    show()