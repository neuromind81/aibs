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

        self.blur = 3
        self.zoom = 0
        self.ledthresh = 233
        self.pupilthresh = 246
        self.ledsize = [34,81]
        self.pupilsize = [330,929]

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
        f0 = self.cam.getImage()
        self.width,self.height = f0.width,f0.height

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
        thetax,thetay = self.gt.gazePix(x),self.gt.gazePix(y)
        return int(thetax),int(thetay)

    def nextFrame(self):
        """GETS NEXT FRAME AND PROCESSES IT"""

        if self._disp.isNotDone():
            i = self.cam.getImage() #get camera image

            if self._framecount%10==0:
                #if i want to do something every N frames
                self._framecount=0    

            #GREYSCALE
            i = i.grayscale()

            #ZOOM?
            if self.zoom is not 0:
                z = self.zoom
                i = i.regionSelect(int(self.width/100*self.zoom),int(self.height/100*self.zoom),
                    int(self.width-self.width/100*self.zoom),int(self.height-self.height/100*self.zoom))
                
            #BLUR?
            if self.blur is not 0:
                i = i.blur(window=(self.blur,self.blur))

            #EQUALIZE
            i = i.equalize()

            #FIND LED
            binary = i.binarize(thresh=self.ledthresh).invert() #get LED
            led = i.findBlobsFromMask(binary,minsize=self.ledsize[0],
                maxsize=self.ledsize[1])
            if led:
                if(len(led)>0): # if we got a blob
                    led[-1].draw(color=Color.GREEN) # the -1 blob is the largest blob - draw it
                    self.led = [led[-1].x,led[-1].y]
                    locationStr = "LED: ("+str(self.led[0])+","+str(self.led[1])+")"
                    # write the led's centroid to the image
                    i.dl().text(locationStr,(0,0),color=Color.GREEN)
            
            #FIND PUPIL
            binary = i.invert().binarize(thresh=self.pupilthresh).invert()
            pupil = i.findBlobsFromMask(binary,minsize=self.pupilsize[0],
                maxsize=self.pupilsize[1])
            if pupil:
                if(len(pupil)>0): # if we got a blob
                    pupil[-1].draw(color=Color.RED) # the -1 blob is the largest blob - draw it
                    self.pupil = [pupil[-1].x,pupil[-1].y]
                    locationStr = "PUPIL: ("+str(self.pupil[0])+","+str(self.pupil[1])+")"
                    # write the pupil's centroid to the image
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

            #UPDATE FRAMECOUNT
            self._framecount += 1     

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
        self.leddistance=5 #distance of LED from mouse
        self.ledx=0 #x position of LED relative to mouse
        self.ledy=0 #y position of LED relative to mouse
        self.imgw=640
        self.imgh=480
        self.imgdiag=np.sqrt((self.imgw**2)+(self.imgh**2))
        self.camfov=90
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
    gt = GazeTracker()
    #print gt.gazeAngle(10)
    print gt.gazePix(-20)

if __name__ == '__main__':
    main()