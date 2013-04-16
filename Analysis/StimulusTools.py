# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 16:19:34 2013

@author: derricw
"""

import scipy.io as sio


class StimulusMatFile(object):
    
    def __init__(self, path = None):
        if path is not None: self.loadMat(path)
        
    def loadMat(self,path):
        self.data = sio.loadmat(path)
        for k,v in self.data.iteritems():
            setattr(self,k,v)
        
    def getOffScreenFrames(self):
        objectwidthDeg = int(self.terrain['objectwidthDeg'])
        
        for x in self.posx:
            pass
          
          
def main():
    path = r"C:\ForagingLogs\130415161217-test.mat"
    mat = StimulusMatFile(path)
    return mat
          
if __name__ == "__main__":
    mat = main()