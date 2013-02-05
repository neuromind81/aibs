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
import time
import datetime
import scipy
import numpy
import pylab
import os
from decimal import Decimal
from aibs.Terrain import Terrain
from aibs.ailogger import ailogger
from aibs.Core import buildSweepTable
try:
    from aibs.Encoder import Encoder
    from aibs.Reward import Reward
except:
    print "Could not import Encoder or Reward objects."



class prettyfloat(float):
    """ Prettier format for float text output. """
    def __repr__(self):
        return "%0.4f" % self


class Foraging(object):

    def __init__(self, window, params, terrain = None, bgSweep = None, fgSweep = None, bgStim = None, fgStim = None, fgFrame = None, bgFrame = None):
        
        """ Constructor.  Builds Foraging experiment and prepares for run() """
        # GENERIC PARAMETERS (generate them as properties of this instance of Foraging; they don't change)
        self.params = params
        for k,v in self.params.iteritems():
            setattr(self,k,v)
            
            
        #MONITOR INFO
        ##TODO: Get monitor from script
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
        self.bgsweeptable, self.bgsweeporder, self.bgdimnames = buildSweepTable(self.bgSweep, self.runs, self.blanksweeps)
        self.fgsweeptable, self.fgsweeporder, self.fgdimnames = None,None,None #foreground sweeps not implemented yet
        print self.bgsweeporder
        
        #STIMULUS OBJECTS
        self.bgStim = bgStim
        self.fgStim = fgStim
        
        #INITIALIZE TERRAIN
        self.terrain = terrain
        self.offscreen = self.off_screen_distance(self.terrain.orientation)
        self.updateTerrain()
        
        #INITIALIZE ENCODER
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
            self.encoder = None
        self.x = 0
        self.lastDx = 0
        self.crossedZero = True
        
        #INITIALIZE REWARD
        ##TODO: read args from config file
        try:
            self.reward = Reward('Dev1',1,0) 
            self.reward.start()
        except:
            print "Could not initialize Reward.  Ensure that NI is connected properly."
            self.ni = False
            self.reward = None
        self.framescorrect = 0
        

        
    def updateBackground(self, sweepi):
        """ Updates the background stimulus based on its sweep number. """
        if self.bgStim is not None:
            if sweepi is not -1: #regular sweep
                self.bgStim.setOpacity(1.0)
                for k,v in zip(self.bgdimnames, self.bgsweeptable[sweepi]):
                    try: #parameter is a proper stimulus property
                        exec("self.bgStim.set" + k + "(" + str(v) + ")")
                    except: #paramter is not a proper stimulus property
                        if k == "TF": #special case for temporal freqency
                            self.bgFrame[k] = v
                        else: print "Sweep parameter is incorrectly formatted:", k, v
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
        
    def checkTerrain(self):
        """ Determines if a reward should be given """
        if self.terrain.iscorrect:
            if self.terrain.windowwidth > self.x > -self.terrain.windowwidth:
                if self.framescorrect > self.terrain.selectiontime:
                    if self.ni: self.reward.reward()
                    self.rewards.append((time.clock(), self.vsynccount))
                    self.terrain.iscorrect = False
                self.framescorrect += 1
            else:
                self.framescorrect = 0
                
    def updateTerrain(self):
        """ Updates terrain variables and logs current instance """
        ##TODO: update terrain to allow for discrimination besides color and orientation
        try: #because some types of stimulus won't let you change color.  I don't like how this works.
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
        """ Checks encoder values and tweaks foreground object position based on speedgain. """
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
            if self.crossedZero == True: #ensures that the mouse has crossed zero
                self.terrain.new() # gets new object
                self.updateTerrain()
                self.laps.append((time.clock(), self.vsynccount))
                self.crossedZero = False
            self.x = -self.wwidth/2-self.offscreen
        elif self.x < -self.wwidth/2-self.offscreen:
            self.x = -self.wwidth/2 + self.terrain.lapdistance + self.offscreen
            #perhaps do something here so that something happens when they go backwards
        if -100 < self.x < 100:
            self.crossedZero = True
        self.posx.append(int(self.x))
        self.dx.append(self.lastDx)
        
    def off_screen_distance(self, orientation = 0):
        """Gets off screen distance using formula to compensate for orientation of object """
        x = misc.deg2pix(self.terrain.objectwidthDeg, self.monitor) # converts width of object to pixels from degrees
        dist = orientation/45*(numpy.sqrt(2*(x)**2)-x) + x #pythagorean theorem
        return dist/2 #float divide by two because measurement is from center of object
        
    def printFrameInfo(self):
        """ Prints data about frame times """
        intervalsMS = numpy.array(window.frameIntervals)*1000
        self.intervalsms = intervalsMS
        m=pylab.mean(intervalsMS)
        sd=pylab.std(intervalsMS)
        distString= "Mean=%.1fms,    s.d.=%.1f,    99%%CI=%.1f-%.1f" %(m,sd,m-3*sd,m+3*sd)
        nTotal=len(intervalsMS)
        nDropped=sum(intervalsMS>(1.5*m))
        self.droppedframes = ([x for x in intervalsMS if x > (1.5*m)],[x for x in range(len(intervalsMS)) if intervalsMS[x]>(1.5*m)])
        droppedString = "Dropped/Frames = %i/%i = %.3f%%" %(nDropped,nTotal,nDropped/float(nTotal)*100)
        #calculate some values
        print "Vsyncs displayed:",self.vsynccount
        print "Frame interval statistics:", distString
        print "Drop statistics:", droppedString
        
    def cleanup(self):
        """ Destructor """
        #STOP CLOCKS
        self.stoptime = time.clock()
        self.stopdatetime = datetime.datetime.now()
        #DISPLAY SOME STUFF
        print self.sweepsdisplayed, "sweeps completed."
        self.printFrameInfo()
        #LOG INFORMATION
        self.logMeta()
        #CLOSE EVERYTHING
        if self.ni:
            self.encoder.clear()
            self.reward.clear()
        window.close()
        core.quit()
        
    def logMeta(self):
        """ Writes all important information to log. """
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
        log.add(startdatetime = str(self.startdatetime))
        log.add(stopdatetime = str(self.stopdatetime))
        log.add(starttime = self.starttime)
        log.add(stoptime = self.stoptime)
        log.add(vsynccount = self.vsynccount)
        log.add(sweeps = self.sweepsdisplayed)
        log.add(laps = self.laps)
        log.add(rewards = self.rewards)
        log.add(terrainlog = self.terrainlog)
        log.add(genericparams = self.params)
        log.add(bgsweep = self.bgSweep)
        log.add(fgsweep = self.fgSweep)
        log.add(bgframe = self.bgFrame)
        log.add(fgframe = self.fgFrame)
        log.add(bgsweeptable = self.bgsweeptable)
        log.add(bgsweeporder = self.bgsweeporder)
        log.add(bgdimnames = self.bgdimnames)
        log.add(fgsweeptable = self.fgsweeptable)
        log.add(fgsweeporder = self.fgsweeporder)
        log.add(fgdimnames = self.fgdimnames)
        log.add(terrain = self.terrain.__dict__)
        log.add(reward = repr(self.reward))
        log.add(encoder = repr(self.encoder))
        log.add(posx = self.posx)
        log.add(dx = map(prettyfloat,self.dx))
        log.add(vsyncintervals = map(prettyfloat,self.intervalsms.tolist()))
        log.add(droppedframes = self.droppedframes)
        log.close()
        
        

    def run(self):
        """ Main stimuilus setup and loop """
        #START CLOCKS
        self.startdatetime = datetime.datetime.now()
        self.starttime = time.clock()
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
        window.clearBuffer()
        for vsync in range(int(self.postexpsec*60)):
            window.flip()
            self.vsynccount += 1
        if self.bgStim is not None: self.bgStim.setOpacity(1.0)
        window.setRecordFrameIntervals(False) #stop recording frame intervals
        
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
    params['rewardtime'] = 0.03 #length of reward for mouse
    params['logdir'] = "C:\\ForagingLogs\\" #where to put the log
    params['backupdir'] = "" #backup to network
    params['mousename'] = "Spock" #name of the mouse
    params['userid'] = "derricw" #name of the user
    params['task'] = "Virtual Foraging" #task type
    params['stage'] = "idkwhatthismeans" #stage
    params['protocol'] = "" #implemented later
    params['nidevice']='Dev1' #NI device name
    params['rewardline']=0 #NI DO line
    params['rewardport']=1 #NI DO port
    params['encodervinchannel']=1 #NI Vin channel
    params['encodervsigchannel']=2 #NI Vsig channel
    params['blanksweeps']=3 #blank sweep every x sweeps
    params['bgcolor']='gray' #background color
    
    #TERRAIN CREATION AND PARAMETERS (see Terrain for additional parameters)
    terrain = Terrain(['color','orientation'])
    terrain.objectwidthDeg = 10
    terrain.colormatters = False
    terrain.orientation = 45
    
    #SET CONSOLE OUTPUT LEVEL, INITIALIZE WINDOWS
    logging.console.setLevel(logging.DEBUG) #uncommet for diagnostics
    window = visual.Window(units='norm',monitor='testMonitor', fullscr = True, screen = 0)
    window.setColor(params['bgcolor'])
    
    #CREATE BACKGROUND STIMULUS
    
    grating = visual.GratingStim(window,tex="sin",mask="None",texRes=64,
           size=[80,80], sf=1, ori = 0, name='grating', autoLog=False, units = 'deg')
    
    '''
    noiseTexture = scipy.random.rand(16,16)*2.0-1
    noise = visual.GratingStim(window, tex=noiseTexture, 
        units='pix', size = [1280,1024],
        interpolate=False,
        autoLog=False)
    '''
           
    #CREATE BACKGROUND FRAME PARAMETERS (what changes between frames and how much)
    bgFrame = {}
    
    #CREATE BACKGROUND SWEEP PARAMETERS (what changes between sweeps, and in what order)  
    bgSweep = {}
    
    bgSweep['Ori'] = ([0,45],1)
    bgSweep['SF'] = ([1,2],3)
    bgSweep['Contrast'] = ([0.5,1],0)
    bgSweep['TF'] = ([1],2)
    
    #CREATE FOREGROUND STIMULUS
    monitor = monitors.Monitor('testMonitor')
    box = visual.Rect(window,width = misc.deg2pix(terrain.objectwidthDeg,monitor), height = misc.deg2pix(terrain.objectwidthDeg,monitor), units = 'pix', fillColor = 'black', lineColor = 'black', autoLog=False)
    #img = visual.ImageStim(window, image = "C:\\Users\\derricw\\Pictures\\facepalm.jpg", size = [450,300], units = 'pix', autoLog=False) #creates an image from an image in specified directory
    #CREATE FOREGROUND STIMULUS FRAME PARAMETERS (what changes between frames and how much (BESIDES XPOSITITON WHICH IS AUTOMATIC FOR THIS EXPERIMENT)
    fgFrame = {}
    
    #CREATE FOREGROUND SWEEP PARAMETERS (what changes between sweeps)
    fgSweep = {}

    #CREATE FORAGING CLASS INSTANCE
    f = Foraging(window = window, terrain = terrain, params = params, bgStim = grating, bgFrame = bgFrame, bgSweep = bgSweep, fgStim = box)
    #RUN IT
    f.run()
