# -*- coding: utf-8 -*-

'''
Created on Jan 27, 2013

@author: derricw

Foraging.py

This class is designed to run a foraging behavior experiment which a background and foreground stimulus.
    The animal runs "laps" through a virtual track and until it finds the correct object and puts that
    that object in the center of the screen for a certain amount of frames.

Designed for the psychopy stimulus library.  http://www.psychopy.org/
Other dependencies:
    PyDAQmx  http://pypi.python.org/pypi/PyDAQmx
    aibs  https://github.com/derricw/aibs

Example use:
    
    
    See main() below.



'''
from psychopy import core, visual, event, logging, misc, monitors
import scipy
import numpy
import itertools
import pylab
from aibs.Terrain import Terrain
from aibs.ailogger import ailogger
try:
    from aibs.Encoder import Encoder
    from aibs.Reward import Reward
except:
    pass
import time

class Foraging(object):

    def __init__(self, window, params, terrain = None, bgSweep = None, fgSweep = None, bgStim = None, fgStim = None, fgFrame = None, bgFrame = None):
        
        """ Constructor.  Builds Foraging experiment and prepares for run() """
        # GENERIC PARAMETERS (generate them as properties of this instance of Foraging; they don't change)
        self.params = params
        for k,v in self.params.iteritems():
            setattr(self,k,v)
            
        #MONITOR INFO
        self.wwidth = window.size[0]
        self.wheight = window.size[1]
        self.monitor = monitors.Monitor('testMonitor')
        self.ni = True
        
        
        #SOME STUFF WE WANT TO TRACK AND RECORD
        self.sweepsdisplayed = 0
        self.laps = []
        self.rewards = []
        self.posx = []
        self.dx = []
        self.terrainlog = []
        
        #SWEEP AND FRAME PARAMETERS PASSED IN
        self.bgSweep = bgSweep
        self.fgSweep = fgSweep
        self.bgFrame = bgFrame
        self.fgFrame = fgFrame
        
        #BUILD SWEEP TABLES
        self.bgsweeptable, self.bgsweeporder, self.bgdimnames = self.buildSweepTable(self.bgSweep)
        
        #STIMULUS OBJECTS
        self.bgStim = bgStim
        self.fgStim = fgStim
        #self.fgStim.setPos([0,0])  #or variable?
        
        #INITIALIZE TERRAIN
        self.terrain = terrain
        self.offscreen = self.off_screen_distance(self.terrain.orientation)
        self.updateTerrain()
        
        
        #SET UP ENCODER
        ##TODO: read args from config file
        try:
            self.encoder = Encoder('Dev1',1,2)
            self.encoder.start()
            time.sleep(0.1)
            self.encDeg = self.encoder.getDegrees()
        except:
            print "Could not initialize Encoder.  Ensure that NI is connected properly."
            self.encDeg = 0
            self.ni = False
        self.x = 0
        self.lastDx = 0
        self.crossedZero = True
        
        #SET UP REWARD
        ##TODO: read args from config file
        try:
            self.reward = Reward('Dev1',1,0) 
            self.reward.start()
        except:
            print "Could not initialize Reward.  Ensure that NI is connected properly."
            self.ni = False
        self.framescorrect = 0
        

    def buildSweepTable(self, sweep):
        """ Builds an ordered table of every permutation of input dictionary of tuples. """
        sweepcount = 1
        dimensions = len(sweep)
        dimarray = []
        dimnames = []
        
        for key,values in sweep.iteritems():
            sweepcount *= len(values[0]) # get number of sweeps
        
        for d in range(dimensions):
            for k,v in sweep.iteritems():
                if v[1] == d:
                    dimarray.append(len(v[0])) # get ordered dimenstion array
                    dimnames.append(k) # get ordered name array
                    
        dimlist = [sweep[k][0] for k in dimnames] # get ordered value array
        sweeptable = list(itertools.product(*dimlist)) # get full ordered table
        sweeporder = range(sweepcount)
        return sweeptable, sweeporder, dimnames
        
    def updateBackground(self, sweepi):
        """ Updates the background stimulus based on its sweep number. """
        if self.bgStim is not None:
            for k,v in zip(self.bgdimnames, self.bgsweeptable[sweepi]):
                try: #parameter is a proper stimulus property
                    exec("self.bgStim.set" + k + "(" + str(v) + ")")
                except: #paramter is not a proper stimulus property
                    if k == "TF": #special case for temporal freqency
                        self.bgFrame[k] = v
                    
                
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
        
    def checkTerrain(self):
        """ Determines if a reward should be given """
        if self.terrain.iscorrect:
            if self.terrain.windowwidth > self.x > -self.terrain.windowwidth:
                if self.framescorrect > self.terrain.selectiontime:
                    if self.ni: self.reward.reward()
                    self.rewards.append(time.clock())
                    self.terrain.iscorrect = False
                self.framescorrect += 1
            else:
                self.framescorrect = 0
                
    def updateTerrain(self):
        """ Updates terrain variables and logs current instance """
        ##TODO: update terrain to allow for discrimination besides color and orientation
        try:
            if self.terrain.color == self.terrain.white: 
                self.fgStim.setLineColor('white')
                self.fgStim.setFillColor('white')
            elif self.terrain.color == self.terrain.black:
                self.fgStim.setLineColor('black')
                self.fgStim.setFillColor('black')
        except:
            pass
        self.fgStim.setOri(self.terrain.orientation)
        self.offscreen = self.off_screen_distance(self.terrain.orientation)
        self.terrainlog.append((self.terrain.orientation, self.terrain.color))
                
    def checkEncoder(self):
        """ Checks encoder values and tweaks foreground object position. """
        if self.ni: deg = self.encoder.getDegrees() 
        else: deg = 0
        dx = deg-self.encDeg
        self.encDeg = deg
        if 180 > dx > -180: #encoder hasn't looped
            self.x += dx*self.terrain.speedgain
            self.lastDx = dx
        elif dx >= 180: #encoder has looped forward
            self.x += self.lastDx*self.terrain.speedgain
        elif dx <=-180: #encoder has looped backward
            self.x -= 0-self.lastDx*self.terrain.speedgain
        
        if self.x > (-self.wwidth/2 + self.terrain.lapdistance + self.offscreen):
            if self.crossedZero == True:
                self.terrain.new() # gets new object
                self.updateTerrain()
                self.laps.append((time.clock(), self.vsynccount))
                self.crossedZero = False
            self.x = -self.wwidth/2-self.offscreen
            print self.x, self.terrain.objectwidthDeg, self.offscreen
        elif self.x < -self.wwidth/2-self.offscreen:
            self.x = -self.wwidth/2 + self.terrain.lapdistance + self.offscreen
            #perhaps do something here so that something happens when they go backwards
        if -100 < self.x < 100:
            self.crossedZero = True
        self.posx.append(int(self.x))
        self.dx.append(round(self.lastDx,4))
        
    def off_screen_distance(self, orientation = 0):
        """Gets off screen distance using formula to compensate for orientation of object """
        x = misc.deg2pix(self.terrain.objectwidthDeg, self.monitor) # converts width of object to pixels from degrees
        dist = orientation/45*(numpy.sqrt(2*(x)**2)-x) + x #pythagorean theorem
        return dist/2 #float divide by two because measurement is from center of object
        
    def printFrameInfo(self):
        """ Prints data about frame times """
        intervalsMS = numpy.array(window.frameIntervals)*1000
        m=pylab.mean(intervalsMS)
        sd=pylab.std(intervalsMS)
        distString= "Mean=%.1fms,    s.d.=%.1f,    99%%CI=%.1f-%.1f" %(m,sd,m-3*sd,m+3*sd)
        nTotal=len(intervalsMS)
        nDropped=sum(intervalsMS>(1.5*m))
        droppedString = "Dropped/Frames = %i/%i = %.3f%%" %(nDropped,nTotal,nDropped/float(nTotal))
        #calculate some values
        print "Vsyncs displayed:",self.vsynccount
        print "Frame interval statistics:", distString
        print "Drop statistics:", droppedString
        
        
    def cleanup(self):
        """ Destructor """
        self.printFrameInfo()
        self.logMeta()
        if self.ni:
            self.encoder.clear()
            self.reward.clear()
        window.close()
        core.quit()
        
    def logMeta(self):
        """ Log all relevent data """
        pass

    def run(self):
        """ Main stimuilus loop """
        #CLOCK SETUP
        sweepClock = core.Clock()
        blankClock = core.Clock()
        self.vsynccount = 0
        
        window.setRecordFrameIntervals() #start checking frame intervals
        #PRE EXPERIMENT LOOP
        for vsync in range(int(self.preexpsec*60)):
            window.flip()
            self.vsynccount += 1
        
        #SWEEP LOOPS
        for sweep in self.bgsweeporder:
            self.updateBackground(sweep) #update background sweep parameters
            self.updateForeground(sweep) #update foreground sweep parameters (not implemented)
            
            #MAIN DISPLAY LOOP
            sweepClock.reset() #reset clock every sweep
            for vsync in range(int(self.sweeplength*60)):
                if self.bgStim is not None:
                    self.bgStim.draw()
                    self.updateFrame(vsync)
                if self.fgStim is not None: 
                    self.fgStim.draw()
                    self.checkTerrain()
                    self.checkEncoder()
                    self.fgStim.setPos([self.x,0]) #set fgStim position every frame
                for keys in event.getKeys(timeStamped=True):
                    if keys[0]in ['escape','q']:
                        self.cleanup()
                window.flip()
                self.vsynccount += 1
            self.sweepsdisplayed += 1
            
            #POST SWEEP DISPLAY LOOP
            blankClock.reset() #reset clock 
            if self.bgStim is not None: self.bgStim.setOpacity(0.0)
            for vsync in range(int(self.postsweepsec*60)):
                if self.bgStim is not None: self.bgStim.draw()
                if self.fgStim is not None: 
                    self.fgStim.draw()
                    self.checkTerrain()
                    self.checkEncoder()
                    self.fgStim.setPos([self.x,0])
                window.flip()
                self.vsynccount += 1
            if self.bgStim is not None: self.bgStim.setOpacity(1.0)
            
            
        #POST EXPERIMENT LOOP
        blankClock.reset() #reset clock
        if self.bgStim is not None: self.bgStim.setOpacity(0.0)
        if self.fgStim is not None: self.fgStim.setOpacity(0.0)
        for vsync in range(int(self.postexpsec*60)):
            if self.bgStim is not None: self.bgStim.draw()
            if self.fgStim is not None: self.fgStim.draw()
            window.flip()
            self.vsynccount += 1
        if self.bgStim is not None: self.bgStim.setOpacity(1.0)
        window.setRecordFrameIntervals(False) #stop recording frame intervals
        
        #POST EXP CLEANUP
        self.cleanup()
    
if __name__ == "__main__":
    
    #GENERIC PARAMETERS
    params = {}
    params['preexpsec'] = 2 #seconds at the start of the experiment
    params['postexpsec'] = 2 #seconds at the end of the experiment
    params['sweeplength'] = 2 #length of sweeps
    params['postsweepsec'] = 1 #black period after sweeps (foreground remains)
    params['rewardtime'] = 0.03 #length of reward for mouse
    
    #TERRAIN CREATION AND PARAMETERS
    terrain = Terrain(['color','orientation'])
    terrain.objectwidthDeg = 10
    terrain.colormatters = False
    terrain.orientation = 45
    
    #SET CONSOLE OUTPUT LEVEL, INITIALIZE WINDOWS
    logging.console.setLevel(logging.DEBUG) #uncommet for diagnostics
    window = visual.Window(units='norm',monitor='testMonitor', fullscr = True, screen = 0)
    
    #CREATE BACKGROUND STIMULUS
    grating = visual.GratingStim(window,tex="sin",mask="None",texRes=64,
           size=[80,80], sf=1, ori = 0, name='grating', autoLog=False, units = 'deg')
           
    #CREATE BACKGROUND FRAME PARAMETERS (what changes between frames and how much)
    bgFrame = {}
    
    #CREATE BACKGROUND SWEEP PARAMETERS (what changes between sweeps)
    bgSweep = {}
    bgSweep['Ori'] = ([0,15,30,45],1)
    bgSweep['SF'] = ([1],3)
    bgSweep['Contrast'] = ([1],0)
    bgSweep['TF'] = ([1],2)
    
    #CREATE FOREGROUND STIMULUS
    monitor = monitors.Monitor('testMonitor')
    #box = visual.Rect(window,width = misc.deg2pix(terrain.objectwidthDeg,monitor), height = misc.deg2pix(terrain.objectwidthDeg,monitor), units = 'pix', fillColor = 'black', lineColor = 'black', autoLog=False)
    img = visual.ImageStim(window, image = "C:\Users\derricw\Pictures\shatner.jpg", size = [450,416], units = 'pix', autoLog=False) #creates an image from an image in specified directory
    
    #CREATE FOREGROUND STIMULUS FRAME PARAMETERS (what changes between frames and how much (BESIDES POSITITON WHICH IS AUTOMATIC FOR THIS EXPERIMENT)
    fgFrame = {}
    
    #CREATE FOREGROUND SWEEP PARAMETERS (what changes between sweeps)
    fgSweep = {}

    #CREATE FORAGING CLASS INSTANCE
    f = Foraging(window = window, terrain = terrain, params = params, bgStim = grating, bgFrame = bgFrame, bgSweep = bgSweep, fgStim = img)
    #RUN IT
    f.run()
