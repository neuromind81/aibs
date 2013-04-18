# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 16:19:34 2013

@author: derricw
"""

import scipy.io as sio
from numpy import *
from psychopy import monitors,misc

class StimulusMatFile(object):
    
    def __init__(self, path = None):
        """Creates a mat file object for outputing various values for
            data analysis.
            after loading a .mat file, self.data contains a dictionary of all values.
            """
        if path is not None: self.loadMat(path)
        
    def loadMat(self,path):
        """ Loads a .mat file """
        self.data = sio.loadmat(path)
        for k,v in self.data.iteritems():
            setattr(self,k,v)
        
    def getOffScreenFrames(self):
        """ Returns a list of frames when the foreground stimulus is offscreen """
        objectwidthDeg = int(self.terrain['objectwidthDeg'])
        mon = monitors.Monitors('testMonitor')
        objectwidthPix = misc.deg2pix(objectwidthDeg,mon)
        
        
        posx = array(self.posx)
          
def main():
    path = r"C:\ForagingLogs\130415161217-test.mat"
    mat = StimulusMatFile(path)
    return mat
          
if __name__ == "__main__":
    mat = main()
