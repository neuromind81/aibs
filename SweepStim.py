# -*- coding: utf-8 -*-

'''
Created on Jan 27, 2013

@author: derricw

SweepStim.py

This class is designed to display a stimulus in sweeps, based on passed parameters.

Designed for the psychopy stimulus library.  http://www.psychopy.org/
Other dependencies:
    PyDAQmx  http://pypi.python.org/pypi/PyDAQmx
    aibs  https://github.com/derricw/aibs

Example use:
    
    See main() below for an example that displays gratings.



'''
from psychopy import core, visual, event, logging, misc, monitors
import time
import datetime
import scipy
import numpy
import pylab
import os
import random
from decimal import Decimal
from aibs.ailogger import ailogger, npdict2listdict, removenparrays
from aibs.Core import buildSweepTable, getMonitorInfo
try:
    from aibs.DigitalIODAQ import DigitalOutput
except Exception, e:
    print "No NI boards found.",e


class prettyfloat(float):
    """ Prettier format for float text output. """
    def __repr__(self):
        return "%0.4f" % self


class SweepStim(object):

    def __init__(self, window, params, bgSweep = None, fgSweep = None, bgStim = None, fgStim = None, fgFrame = None, bgFrame = None):
        
        """ Constructor.  Builds SweepStim experiment and prepares for run() """
        # GENERIC PARAMETERS (generate them as properties of this instance of Gratings; they don't change)
        self.params = params
        for k,v in self.params.iteritems():
            setattr(self,k,v)
            
        #MONITOR INFO
        ##TODO: Get monitor from script
        self.window = window
        self.wwidth = window.size[0]
        self.wheight = window.size[1]
        self.monitor = monitors.Monitor('testMonitor')
        self.ni = True
        
        #CREATE SYNC SQUARE (used for frame time measurement via photodiode)
        if self.syncsqr:
            self.sync = visual.GratingStim(self.window, color = 1, tex=None, size = (75,75), pos = self.syncsqrloc, units = 'pix', autoLog=False)
            self.syncsqrcolor = 1 # STARTS WHITE
        
        #SOME STUFF WE WANT TO TRACK AND RECORD
        self.sweepsdisplayed = 0
        
        #SWEEP AND FRAME PARAMETERS PASSED IN
        self.bgSweep = bgSweep
        self.fgSweep = fgSweep
        self.bgFrame = bgFrame
        self.fgFrame = fgFrame
        
        #BUILD SWEEP TABLES
        self.bgsweeptable, self.bgsweeporder, self.bgdimnames = buildSweepTable(self.bgSweep, self.runs, self.blanksweeps)
        self.fgsweeptable, self.fgsweeporder, self.fgdimnames = None,None,None #foreground sweeps not implemented yet
        if self.shuffle: random.shuffle(self.bgsweeporder)
        #print "BG sweep order: ", self.bgsweeporder
        
        #STIMULUS OBJECTS
        self.bgStim = bgStim
        self.fgStim = fgStim
        
        #INITIALIZE NIDAQ
        try:
            self.dOut = DigitalOutput(self.nidevice)  # device should be read from a config file
            self.dOut.StartTask()
            self.ni = True
            self.sweepBit = 0
            self.frameBit = 1
        except:
            self.ni = False
            print "NIDAQ could not be initialized! No frame/sweep data will be output."
        
    def updateBackground(self, sweepi):
        """ Updates the background stimulus based on its sweep number. """
        if self.bgStim is not None:
            if sweepi is not -1: #regular sweep
                self.bgStim.setOpacity(1.0)
                for k,v in zip(self.bgdimnames, self.bgsweeptable[sweepi]):
                    try: #parameter is a proper stimulus property
                        exec("self.bgStim.set" + k + "(" + str(v) + ")")
                    except Exception, e: #paramter is not a proper stimulus property
                        if k == "TF": #special case for temporal freqency
                            self.bgFrame[k] = v
                        elif k == "Tex": #special case for textures (fix later)
                            self.bgStim.setTex(v)
                        elif k == "Image": #special case for images
                            self.bgStim.setImage(v)
                        elif k == "PosX": #special case for x position
                            self.bgStim.setPos((v,self.bgStim.pos[1]))
                        elif k == "PosY": #special case for y position
                            self.bgStim.setPos((self.bgStim.pos[0],v))
                        else: print "Sweep parameter is incorrectly formatted:", k, v, e
            else: self.bgStim.setOpacity(0.0) #blank sweep
                
    def updateForeground(self, sweepi):
        """ Updates the foreground stimulus based on its sweep number.  UNIMPLIMENTED."""
        pass
        
    def updateFrame(self, vsync):
        """ Updates frame with any item that is to be modulated per frame. """
        if self.bgStim is not None:
            for k,v in self.bgFrame.iteritems():
                try: #parameter is a proper stimulus property
                    exec("self.bgStim.set" + k + "(" + str(v) + ")")
                except: #parameter is not a proper stimulus property
                    if k == "TF": #special case for temporal frequency
                        self.bgStim.setPhase(v*vsync/60.0)
                    else: print "No parameter called: ", k
                    
    def flipSyncSqr(self):
        """ Flips the sync square. """
        self.sync.setColor(self.syncsqrcolor)
        self.sync.draw()
        self.syncsqrcolor = -self.syncsqrcolor
        
    def printFrameInfo(self):
        """ Prints data about frame times """
        intervalsMS = numpy.array(self.window.frameIntervals)*1000
        self.intervalsms = intervalsMS
        m=pylab.mean(intervalsMS)
        sd=pylab.std(intervalsMS)
        distString= "Mean=%.1fms,    s.d.=%.1f,    99%%CI=%.1f-%.1f" %(m,sd,m-3*sd,m+3*sd)
        nTotal=len(intervalsMS)
        nDropped=sum(intervalsMS>(1.5*m))
        self.droppedframes = ([x for x in intervalsMS if x > (1.5*m)],[x for x in range(len(intervalsMS)) if intervalsMS[x]>(1.5*m)])
        droppedString = "Dropped/Frames = %i/%i = %.3f%%" %(nDropped,nTotal,nDropped/float(nTotal)*100)
        #calculate some values
        print "Actual vsyncs displayed:",self.vsynccount
        print "Frame interval statistics:", distString
        print "Drop statistics:", droppedString
        
    def printExpInfo(self):
        """ Prints expected experiment duration, frames, etc. """
        exptimesec = (self.preexpsec + (self.sweeplength + self.postsweepsec)*len(self.bgsweeporder) + self.postexpsec)
        timestr = str(datetime.timedelta(seconds=exptimesec))
        print "Expected experiment duration:", timestr
        print "Expected sweeps:", str(len(self.bgsweeporder))
        print "Expected vsyncs:", str(exptimesec*60)

    def cleanup(self):
        """ Destructor """
        #STOP CLOCKS
        self.stoptime = time.clock()
        timestr = str(datetime.timedelta(seconds = (self.stoptime-self.starttime)))
        print "Actual experiment duration:", timestr
        self.stopdatetime = datetime.datetime.now()
        #DISPLAY SOME STUFF
        print "Actual sweeps completed:", str(self.sweepsdisplayed)
        self.printFrameInfo()
        #LOG INFORMATION
        self.logMeta()
        #CLOSE EVERYTHING
        if self.ni:
            self.dOut.WriteBit(self.sweepBit, 0) #ensure sweep bit is low
            self.dOut.WriteBit(self.frameBit, 0) #ensure frame bit is low
            self.dOut.ClearTask() #clear NIDAQ
        self.window.close()
        core.quit()
        
    def logMeta(self):
        """ Writes all important information to log. """
        ##TODO: Think of a better way to do this, or move it out of this class somehow.
        dir = self.logdir
        file = self.mousename + ".log" #logger automatically appends timestamp
        path = os.path.join(dir,file)
        log = ailogger(path)
        log.add(mousename = self.mousename)
        log.add(userid = self.userid)
        log.add(task = self.task)
        log.add(stage = self.stage)
        log.add(protocol = self.protocol)
        log.add(logdir = self.logdir)
        log.add(backupdir = self.backupdir)
        log.add(monitor = getMonitorInfo(self.monitor))
        log.add(startdatetime = str(self.startdatetime))
        log.add(stopdatetime = str(self.stopdatetime))
        log.add(starttime = self.starttime)
        log.add(stoptime = self.stoptime)
        log.add(vsynccount = self.vsynccount)
        log.add(sweeps = self.sweepsdisplayed)
        log.add(genericparams = self.params)
        log.add(runs = self.runs)
        log.add(blanksweeps = self.blanksweeps)
        log.add(bgsweep = npdict2listdict(self.bgSweep))
        log.add(fgsweep = self.fgSweep)
        log.add(bgframe = self.bgFrame)
        log.add(fgframe = self.fgFrame)
        log.add(bgsweeptable = removenparrays(self.bgsweeptable))
        log.add(bgsweeporder = self.bgsweeporder)
        log.add(bgdimnames = self.bgdimnames)
        log.add(fgsweeptable = self.fgsweeptable)
        log.add(fgsweeporder = self.fgsweeporder)
        log.add(fgdimnames = self.fgdimnames)
        log.add(vsyncintervals = map(prettyfloat,self.intervalsms.tolist()))
        log.add(droppedframes = self.droppedframes)
        log.close()
        
    def flip(self):
        """ Flips display and sets frame bits. """
        if self.ni: self.dOut.WriteBit(self.frameBit, 1) #set frame bit high
        self.window.flip() # flips display
        if self.ni: self.dOut.WriteBit(self.frameBit, 0) #set frame bit low

    def run(self):
        """ Main stimuilus setup and loop """
        #FLIP FOR A BIT TO GET READY FOR FIRST FRAME
        for i in range(30):
            self.window.flip()
        
        #PRE EXPERIMENT INFO PRINT
        self.printExpInfo()

        #START CLOCKS
        self.startdatetime = datetime.datetime.now()
        self.starttime = time.clock()
        self.vsynccount = 0
        self.window.setRecordFrameIntervals() #start checking frame intervals
        
        #PRE EXPERIMENT LOOP
        for vsync in range(int(self.preexpsec*60)):
            if self.syncsqr: self.flipSyncSqr()
            self.flip()
            self.vsynccount += 1
        
        #SWEEP LOOPS
        for sweep in self.bgsweeporder:
            self.updateBackground(sweep) #update background sweep parameters
            self.updateForeground(sweep) #update foreground sweep parameters (not implemented)
            if self.ni: self.dOut.WriteBit(self.sweepBit, 1) # sets sweep bit high on NIDAQ
            
            #MAIN DISPLAY LOOP
            for vsync in range(int(self.sweeplength*60)):
                if self.bgStim is not None:
                    self.bgStim.draw()
                    self.updateFrame(vsync)
                if self.fgStim is not None: self.fgStim.draw()
                for keys in event.getKeys(timeStamped=True):
                    if keys[0]in ['escape','q']:
                        self.cleanup()
                if self.syncsqr: self.flipSyncSqr()
                self.flip()
                self.vsynccount += 1
            self.sweepsdisplayed += 1
            if self.ni: self.dOut.WriteBit(self.sweepBit, 0) # sets sweep bit low on NIDAQ
            
            #POST SWEEP DISPLAY LOOP
            for vsync in range(int(self.postsweepsec*60)):
                if self.syncsqr: self.flipSyncSqr()
                self.flip()
                self.vsynccount += 1
            
            
        #POST EXPERIMENT LOOP
        for vsync in range(int(self.postexpsec*60)):
            if self.syncsqr: self.flipSyncSqr()
            self.flip()
            self.vsynccount += 1
        self.window.setRecordFrameIntervals(False) #stop recording frame intervals
        
        #POST EXP CLEANUP (stops clocks, cleans up windows, etc)
        self.cleanup()
    
if __name__ == "__main__":
    
    """
    This is a sample script that sets up a basic experiment.  This should be performed by the GUI.
    """
    
    
    #GENERIC PARAMETERS (should be passed by GUI, some of which have been read from config file)
    params = {}
    params['runs'] = 1 #number of runs
    params['shuffle'] = False #shuffle sweep tables
    params['preexpsec'] = 2 #seconds at the start of the experiment
    params['postexpsec'] = 2 #seconds at the end of the experiment
    params['sweeplength'] = 2 #length of sweeps
    params['postsweepsec'] = 1 #black period after sweeps (foreground remains)
    params['logdir'] = "C:\\ExperimentLogs\\" #where to put the log
    params['backupdir'] = "" #backup to network
    params['mousename'] = "Spock" #name of the mouse
    params['userid'] = "derricw" #name of the user
    params['task'] = "" #task type
    params['stage'] = "idkwhatthismeans" #stage
    params['protocol'] = "" #implemented later
    params['nidevice']='Dev1' #NI device name
    params['blanksweeps']=3 #blank sweep every x sweeps
    params['bgcolor']='gray' #background color
    params['syncsqr']=True #display a flashing square for synchronization
    params['syncsqrloc']=(-600,-350)
    
    
    #SET CONSOLE OUTPUT LEVEL, INITIALIZE WINDOWS
    #logging.console.setLevel(logging.DEBUG) #uncommet for diagnostics
    window = visual.Window(units='norm',monitor='testMonitor', fullscr = True, screen = 0, waitBlanking=False)
    window.setColor(params['bgcolor'])
    
    #CREATE BACKGROUND STIMULUS
    
    grating = visual.GratingStim(window,tex="sin",mask="None",texRes=512,
           size=[80,80], sf=1, ori = 0, name='grating', autoLog=False, units = 'deg')
           
    #CREATE BACKGROUND FRAME PARAMETERS (what changes between frames and how much)
    bgFrame = {}
    
    #CREATE BACKGROUND SWEEP PARAMETERS (what changes between sweeps, and in what order)
    bgSweep = {}
    
    bgSweep['Ori'] = ([0,45],1)
    bgSweep['SF'] = ([0.5,1],3)
    bgSweep['Contrast'] = ([0.5,1],0)
    bgSweep['TF'] = ([1],2)
    
    #CREATE FOREGROUND STIMULUS (none for basic gratings experiment)
    
    
    #CREATE FOREGROUND STIMULUS FRAME PARAMETERS (what changes between frames and how much (BESIDES XPOSITITON WHICH IS AUTOMATIC FOR THIS EXPERIMENT)
    fgFrame = {}
    
    #CREATE FOREGROUND SWEEP PARAMETERS (what changes between sweeps)
    fgSweep = {}

    #CREATE FORAGING CLASS INSTANCE
    g = SweepStim(window = window, params = params, bgStim = grating, bgFrame = bgFrame, bgSweep = bgSweep, fgStim = None)
    #RUN IT
    g.run()
