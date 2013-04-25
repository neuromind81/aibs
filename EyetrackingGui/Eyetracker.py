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
import platform


class Eyetracker(object):
    def __init__(self):

        self._framecount = 0

        self.camproperties = {
            'hue':248140158.0,
            'saturation': 83.0,
            'brightness': 100.0, 
            'height': 480, 
            'width': 640, 
            'gain': 248140158.0, 
            'contrast': 10.0, 
            'exposure': -6.0    
        }

        self.blur = 0
        self.zoom = 0
        self.ledthresh = 240
        self.pupilthresh = 225
        self.ledsize = [20,50]
        self.pupilsize = [300,700]

        #locations
        

        #create window
        
        #self.cam = Camera(prop_set=self.camproperties)
        if (platform.system()=="Linux"):
            print "Running on Linux, can't change cam properties..."
        else:
            try:
                for p in self.camproperties.keys():
                    if p in self.cam.prop_map:
                        self.setCamProp(p)
            except:
                print "Couldn't set initial camera properties"
        
        self.cam = VirtualCamera(r"res/mouseeye.png",'image')

        self._disp = Display()

        self._tick = time.clock()
        self._tock = time.clock()

        #get image size
        f0 = self.cam.getImage()
        self.width,self.height = f0.width,f0.height

    def setCamProp(self,prop):
        """Sets a camera property"""
        cv.SetCaptureProperty(self.cam.capture,
            self.cam.prop_map[prop], self.camproperties[prop])


    def nextFrame(self):
        #TEST
        #self._setCamProp('exposure') #should work on windows

        if self._disp.isNotDone():
            i = self.cam.getImage() #get camera image

            if self._framecount%10==0:
                #if i want to do something every N frames
                self._framecount=0
                pass     

            #GREYSCALE/NORMALIZE
            i = i.grayscale().equalize()

            #ZOOM?
            if self.zoom is not 0:
                z = self.zoom
                i = i.regionSelect(z,z,self.width-z,self.height-z)

            #BLUR?
            if self.blur is not 0:
                i = i.blur(window=(self.blur,self.blur))

            #FIND LED
            binary = i.binarize(thresh=self.ledthresh).invert() #get LED
            led = i.findBlobsFromMask(binary,minsize=self.ledsize[0],
                maxsize=self.ledsize[1])
            if led:
                if(len(led)>0): # if we got a blob
                    led[-1].draw(color=Color.GREEN) # the -1 blob is the largest blob - draw it
                    locationStr = "LED: ("+str(led[-1].x)+","+str(led[-1].y)+")"
                    # write the blob's centroid to the image
                    i.dl().text(locationStr,(0,0),color=Color.GREEN)
            
            #FIND PUPIL
            binary = i.invert().binarize(thresh=self.pupilthresh).invert()
            pupil = i.findBlobsFromMask(binary,minsize=self.pupilsize[0],
                maxsize=self.pupilsize[1])
            if pupil:
                if(len(pupil)>0): # if we got a blob
                    pupil[-1].draw(color=Color.RED) # the -1 blob is the largest blob - draw it
                    locationStr = "PUPIL: ("+str(pupil[-1].x)+","+str(pupil[-1].y)+")"
                    # write the blob's centroid to the image
                    i.dl().text(locationStr,(0,10),color=Color.RED)


            #DRAW FPS
            try:
                self._tock = int(1/(time.clock()-self._tick))
            except:
                pass
            self._tick = time.clock()
            i.drawText("FPS: "+str(self._tock),0,i.height-10)

            #SHOW IMAGE
            i.save(self._disp)

            #Update framecount
            self._framecount += 1     

    def close(self):
        self._disp.quit()