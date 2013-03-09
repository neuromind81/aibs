# -*- coding: utf-8 -*-
"""
Created on Fri Feb 08 13:30:07 2013

@author: derricw
"""

import Image
import os
import numpy as np
import scipy.io as sio


def getWaveform(folder):
    """ Input is a folder containing an ordered sequence of .tif files
        Output is a waveform of the first column of each image. """
    waveform = []
    dirs = [os.path.join(folder,name) for name in os.listdir(folder)]
    for d in dirs:
        files = [f for f in os.listdir(d)]
        for f in files:
            path = os.path.join(d,f)
            print path
            img = Image.open(path)
            width,height = img.size
            pixels = list(img.getdata())
            waveform.extend(pixels[0:len(pixels):width])
    return np.array(waveform)

def getFrameLines(waveform):
    """ GETS THE LINES FROM THE IMAGE SEQUENCE FOR EACH FRAME TICK """
    wfrange = np.ptp(waveform)
    centered = (waveform-wfrange*2/3)[:,0]
    zero_crossings = np.where(np.diff(np.sign(centered)))[0]
    
    zdiff = np.diff(zero_crossings)    
    duplicates = []
    for i in range(len(zdiff)):
        if zdiff[i] < 60:
            duplicates.append(i)
    framelines = np.delete(zero_crossings,duplicates)
    ##TODO: COME UP WITH A MORE RELIABLE WAY TO GET RID OF WINDOW FLASH
    framelines = np.delete(framelines,[0,1])
    startframe= framelines[0]
    endframe = framelines[-1]
    #TODO: NEEDS TO USE AVE LINES/FRAME instead of 132
    ideallines = range(startframe,endframe,132)
    return ideallines
    
def getImageNumbers(waveform):
    """ GETS DATA IMAGE NUMBER FOR EACH STIMULUS FRAME TICK OF A WAVEFORM"""
    imagelines = getFrameLines(waveform)
    imagenumbers = [x/256 for x in imagelines]
    return imagenumbers
    
def processSequence(folder):
    """ PROCESSES A SEQUENCE FROM START TO FINISH """
    data = {}    
    data['waveform'] = getWaveform(folder)
    sio.savemat('waveform.mat',data)
    data = sio.loadmat('waveform.mat')
    data['framelines'] = getFrameLines(data['waveform'])
    data['imgnumbers'] = getImageNumbers(data['waveform'])
    sio.savemat('seqoutput.mat',data)
    
if __name__ == "__main__":
    path = r"C:\Users\derricw\Documents\data130307\images\CA170_130205_a\ch3\sequence"
    processSequence(path)
    