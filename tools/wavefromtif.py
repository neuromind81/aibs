# -*- coding: utf-8 -*-
"""
Created on Fri Feb 08 13:30:07 2013

@author: derricw
"""

import Image
import os
from pylab import *
import scipy
import numpy as np
from scipy.signal import butter, lfilter


def getWaveform(folder):
    files = [f for f in os.listdir(folder)]
    waveform = []
    for f in files:
        path = os.path.join(folder,f)
        print path
        img = Image.open(path)
        width,height = img.size
        pixels = list(img.getdata())
        waveform.extend(pixels[0:len(pixels):width])
    return waveform

def getFrameTimes(waveform):
    
    wfrange = np.ptp(waveform)
    centered = waveform-wfrange/3
    zero_crossings = np.where(np.diff(np.sign(centered)))[0]
    samplesperframe = 256.000
    framespersecond = 31.200
    secondspersample = 1/samplesperframe/framespersecond
    frametimes = zero_crossings*secondspersample
    
    fdiff = np.diff(frametimes)
    duplicates = []
    for i in range(len(fdiff)):
        if fdiff[i] < 0.01:
            duplicates.append(i)
    frametimes = np.delete(frametimes,duplicates)
    return frametimes


if __name__ == "__main__":
    
    folder = r"C:\Users\derricw\Pictures\PDTEST\sequence"
    waveform = getWaveform(folder)
    samplesperframe = 256.000
    secondsperframe = 31.200
    secondspersample = 1/samplesperframe/secondsperframe
    twave = [x/samplesperframe/secondsperframe for x in range(len(waveform))]
    files = [f for f in os.listdir(folder)]
    
    tframe = [x/31.2 for x in range(len(files))]
    midpoint = scipy.average(waveform)
    frame = [midpoint for x in range(len(files))]
    frametimes = getFrameTimes(waveform)
    ftrange = [midpoint for x in range(len(frametimes))]

    plot(twave,waveform,tframe,frame,'rd',frametimes,ftrange,'gd')
    xlabel('time, seconds')
    ylabel('Output (intensity, converted from V')
    title('Photodiode waveform')
    legend(('diode','data frame','stimulus frame'))
    show(False)