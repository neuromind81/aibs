# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 22:02:37 2013

@author: derricw
#------------------------------------------------------------------------------ 
EyeTracker.py
#------------------------------------------------------------------------------ 

Dependencies:
SimpleCV http://simplecv.org/

"""

from SimpleCV import *
from pylab import *


class EyeTracker(object):
    def __init__(self):
        #create window
        
        self.cam = Camera()
        self.disp = Display()


    def run(self):
        #loop through grabbing frames
 
        while self.disp.isNotDone():
            i = self.cam.getImage()
            blobs = i.findBlobs()
            if blobs:
                blobs.draw()
            i.save(self.disp)
            if self.disp.mouseLeft:
                hist = i.hueHistogram()
                plot(hist)
                show()
                break
        

if __name__ == '__main__':
    et = EyeTracker()
    et.run()
