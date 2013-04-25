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
import time

PROPERTIES = {
    'hue':248140158.0,
    'saturation': 83.0,
    'brightness': 100.0, 
    'height': 480.0, 
    'width': 640.0, 
    'gain': 248140158.0, 
    'contrast': 10.0, 
    'exposure': -6.0    
}

class EyeTracker(object):
    def __init__(self):
        #create window
        """
        self.cam = Camera(prop_set=PROPERTIES)
        print self.cam.getAllProperties()
        """
        self.cam = VirtualCamera(r"res/mouseeye.png",'image')

        self.disp = Display()

        self._framecount = 0

    def run(self):
        #loop through grabbing frames
        tick = time.clock()

        bm = BlobMaker() # create the blob extractor

        while self.disp.isNotDone():
            i = self.cam.getImage() #get camera image


            if self._framecount%10==0:
                pass     

            #FIND LED
            binary = i.binarize(thresh=240).invert() #get LED
            led = i.findBlobsFromMask(binary,minsize=20,maxsize=50)
            if led:
                if(len(led)>0): # if we got a blob
                    led[-1].draw() # the -1 blob is the largest blob - draw it
                    locationStr = "LED: ("+str(led[-1].x)+","+str(led[-1].y)+")"
                    # write the blob's centroid to the image
                    i.dl().text(locationStr,(0,0),color=Color.GREEN)
            
            #FIND PUPIL
            binary = i.invert().binarize(thresh=225).invert()
            pupil = i.findBlobsFromMask(binary,minsize=300,maxsize=700)
            if pupil:
                if(len(pupil)>0): # if we got a blob
                    print len(pupil)
                    pupil[-1].draw(color=Color.RED) # the -1 blob is the largest blob - draw it
                    locationStr = "PUPIL: ("+str(pupil[-1].x)+","+str(pupil[-1].y)+")"
                    # write the blob's centroid to the image
                    i.dl().text(locationStr,(0,10),color=Color.RED)


            #DRAW FPS
            tock = 1/(time.clock()-tick)
            tick = time.clock()
            i.drawText("FPS: "+str(tock),0,i.height-10)

            #SHOW IMAGE
            i.save(self.disp)

            #ESCAPE?
            if self.disp.mouseLeft:
                break

            self._framecount += 1     

if __name__ == '__main__':
    et = EyeTracker()
    et.run()
