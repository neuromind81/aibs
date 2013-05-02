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
import numpy as np
import math

def dist2d(p1,p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 +
                     (p2[1] - p1[1]) ** 2) 

class Eyetracker(object):
    def __init__(self):
        """Docstring for Eyetracker"""
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
        self.ledthresh = 253
        self.pupilthresh = 240
        self.ledsize = [1,6]
        self.pupilsize = [7,100]

        self.ledwiggle = 15 #HACK FIX ASAP

        #locations
        self.pupil = [-1,-1]
        self.led = [-1,-1]

        #get cam
        self.getNewCam()

        if (platform.system()=="Linux"):
            print "Running on Linux, can't change cam properties..."
        else:
            try:
                for p in self.camproperties.keys():
                    if p in self.cam.prop_map:
                        self.setCamProp(p)
            except:
                print "Couldn't set initial camera properties"

        self._disp = Display()

        self._tick = time.clock()
        self._tock = time.clock()

        #get image size
        f0 = self.cam.getImage() #get size of image camera is putting out
        self.width,self.height = f0.width,f0.height #initialize image size
        self.maxsize = (self.width,self.height) #get max size

        #ROI
        self.roi = None
        self.up,self.dwn = None,None


        #create a gaze tracker instance
        self.gt = GazeTracker()

    def getNewCam(self):
        #self.cam = Camera(prop_set=self.camproperties) #actual camera
        #print self.cam.getAllProperties()
        #self.cam = VirtualCamera(r"res/mouseeye.png",'image') #virtual camera uses image of mouse eye
        self.cam = VirtualCamera(r'res/video1.wmv','video')

    def setCamProp(self,prop):
        """Sets a camera property"""
        cv.SetCaptureProperty(self.cam.capture,
            self.cam.prop_map[prop], self.camproperties[prop])

    def getTriangle(self):
        return self.led[0]-self.pupil[0],self.led[1]-self.pupil[1]

    def getGaze(self):
        """Returns the monitor pixel of the gaze
            (0,0) is center of screen
        """
        x,y = self.getTriangle()
        thetax,thetay = self.gt.gazeAngle(x),self.gt.gazeAngle(y)
        return int(self.gt.gazePix(thetax)),int(self.gt.gazePix(thetay))

    def nextFrame(self):
        """GETS NEXT FRAME AND PROCESSES IT"""
        ##TODO: SPLIT THIS UP.  SHOULD BE SEVERAL COMPARTMENTALIZED FUNCTIONS
        if self._disp.isNotDone():
            i = self.cam.getImage() #get camera image

            #GREYSCALE
            i = i.grayscale()

            #ROI?
            if self.roi is not None:
                i = i.regionSelect(*self.roi)

            #ZOOM?
            if self.zoom is not 0:
                i = i.regionSelect(int(self.width/100*self.zoom),int(self.height/100*self.zoom),
                    int(self.width-self.width/100*self.zoom),int(self.height-self.height/100*self.zoom))

            #BLUR?
            if self.blur is not 0:
                i = i.blur(window=(self.blur,self.blur))

            #EQUALIZE
            i = i.equalize()

            #FIND LED
            if self._framecount%10==0:
                self._framecount=0    
                binary = i.binarize(thresh=self.ledthresh).invert() #get LED
                led = i.findBlobsFromMask(binary,minsize=self.ledsize[0],
                    maxsize=self.ledsize[1])
                if led:
                    if(len(led)>0): # if we got a blob
                        new = [led[-1].x,led[-1].y]
                        if dist2d(new,self.pupil) < self.ledwiggle:
                            self.led = new
            i.drawCircle(self.led,3,color=Color.GREEN,thickness=1)
            
            #FIND PUPIL
            binary = i.invert().binarize(thresh=self.pupilthresh).invert()
            pupil = i.findBlobsFromMask(binary,minsize=self.pupilsize[0],
                maxsize=self.pupilsize[1])
            if pupil:
                if(len(pupil)>0): # if we got a blob
                    self.pupil = [pupil[-1].x,pupil[-1].y]
            i.drawCircle(self.pupil,4,color=Color.RED,thickness=1)

            #DRAW FPS
            try:
                self._tock = int(1/(time.clock()-self._tick))
            except:
                pass
            self._tick = time.clock()
            i.drawText(str(self._tock),0,i.height-10)

            #SHOW IMAGE
            i.save(self._disp)

            #UPDATE FRAMECOUNT
            self._framecount += 1  

            #HANDLE CLICKS IN DISPLAY
            dwn = self._disp.leftButtonDownPosition()
            up = self._disp.leftButtonUpPosition()
            right = self._disp.rightButtonDownPosition()

            if dwn is not None:
                self.dwn = dwn
            if up is not None:
                self.up = up
            if self.up is not None and self.dwn is not None:
                self.roi = (min(self.dwn[0],self.up[0]),min(self.dwn[1],self.up[1]),
                    max(self.up[0],self.dwn[0]),max(self.up[1],self.dwn[1]))
                self.width,self.height = self.roi[2]-self.roi[0], self.roi[3]-self.roi[1]
                self.dwn,self.up=None,None
            if right is not None:
                self.dwn,self.up,self.roi=None,None,None
                (self.width,self.height)=self.maxsize


    def close(self):
        self._disp.quit()

class GazeTracker(object):
    """docstring for GazeTracker"""
    def __init__(self):
        self.monitorsize=(49,40)
        self.monitorresolution=(1920,1080)
        self.monitordistance=11 #distance of mouse relative to screen
        self.mousex=self.monitorsize[0]/2 #x position of mouse relative to screen
        self.mousey=self.monitorsize[1]/2 #y position of mouse relative to screen
        self.leddistance=3 #distance of LED from mouse
        self.ledx=0 #x position of LED relative to mouse
        self.ledy=0 #y position of LED relative to mouse
        self.imgw=640
        self.imgh=480
        self.imgdiag=np.sqrt((self.imgw**2)+(self.imgh**2))
        self.camfov=150
        self.eyeradius=0.33


    def gazeAngle(self,x):
        """Converts camera pixel distance to monitor angle """
        fovd=self.leddistance*np.tan(np.radians(self.camfov/2))*2
        pixpercm=self.imgdiag/fovd
        xdist=x/pixpercm
        return np.degrees(np.arctan(xdist/self.eyeradius))

    def gazePix(self,angle):
        """Converts gaze angle to monitor pixel"""
        return self.deg2pix(angle)

    def pix2cm(self,pix):
        """Pixels to cm based on monitor properties """
        pixpercm = self.monitorresolution[0]/self.monitorsize[0]
        return pix/pixpercm*1.000

    def pix2deg(self,pix):
        """Pixels to deg based on monitor properties """
        cm = self.pix2cm(pix)
        return self.cm2deg(cm)*1.000

    def deg2pix(self,deg):
        """Degrees to pixels based on monitor properties """
        cm = self.deg2cm(deg)
        return self.cm2pix(cm)

    def deg2cm(self,deg):
        """Degrees to cm based on monitor properties """
        return self.monitordistance*np.tan(np.radians(deg))*1.000
        
    def cm2deg(self,cm):
        """cm to degrees based on monitor properties"""
        return np.degrees(np.arctan(cm/self.monitordistance)*1.000)

    def cm2pix(self,cm):
        """Cm to pix based on monitor properties"""
        pixpercm = self.monitorresolution[0]/self.monitorsize[0]
        return cm*pixpercm*1.000



def main():
    pass

if __name__ == '__main__':
    main()