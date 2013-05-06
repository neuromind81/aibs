# -*- coding: utf-8 -*-

'''
Created on Jan 27, 2013

@author: derricw

Foraging.py

This class is designed to run a foraging behavior experiment which a background and foreground stimulus.
    The animal runs "laps" through a virtual track and until it finds the correct object and puts that
    that object in the center of the screen for a certain amount of frames.
    
Foraging shares and inherits some basic functionality from SweepStim.

Designed for the psychopy stimulus library.  http://www.psychopy.org/
Other dependencies:
    PyDAQmx  http://pypi.python.org/pypi/PyDAQmx
    aibs  https://github.com/derricw/aibs

Example use:
    
    See main() below.

'''
from psychopy import core, visual, event, logging, misc, monitors
from pyglet.window import key
import time
import datetime
import numpy
import os
import random
import sys
from aibs.Terrain import Terrain
from aibs.ailogger import *
from aibs.SweepStim import SweepStim
from aibs.Core import *
try:
    from aibs.Encoder import Encoder
    from aibs.Reward import Reward
except Exception, e:
    print "Could not import Encoder or Reward objects.", e


class Foraging(SweepStim):

    def __init__(self, window, params, terrain = None, bgSweep = {}, fgSweep = {}, bgStim = None, fgStim = None, fgFrame = {}, bgFrame = {}):
        
        """ Constructor.  Builds Foraging experiment and prepares for run() """
        # GENERIC PARAMETERS (generate them as properties of this instance of Foraging; they don't change)
        self.params = params
        for k,v in self.params.iteritems():
            setattr(self,k,v)
        
        #READ CONFIG FILE, SET ATTRIBUTES
        try:
            f = open('foraging.cfg','r')
            for rl in f.readlines():
                (k,v) = rl.split(' = ')
                setattr(self,k,eval(v))
        except Exception,e:
            print "Error reading config file: ",e

        #SET STIMULUS DOMAIN
        self.timedomain = False
        
        #MONITOR INFO
        self.wwidth = window.size[0]
        self.wheight = window.size[1]
        self.monitor = window.monitor

        self.window = window
        self.window.winHandle.set_exclusive_mouse()
        self.window.winHandle.set_exclusive_keyboard()

        #TURN OFF MOUSE
        self.mouse = event.Mouse()
        self.mouse.setVisible(0) 
        #SET OS PRIORITY TO HIGH
        try:
            setpriority()
        except Exception, e:
            print "Could not set OS priority to high.", e
        
        #CREATE SYNCRONIZATION SQUARE (used for precise frame time measurement via photodiode)
        if self.syncsqr:
            self.sync = visual.GratingStim(self.window, tex=None, color = 1, size = (100,100), pos = self.syncsqrloc, units = 'pix', autoLog=False)
            self.syncsqrcolor = 1 #STARTS WHITE
        
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
        if self.shuffle: random.shuffle(self.bgsweeporder)
        print "BG sweep order: ", self.bgsweeporder
        
        #STIMULUS OBJECTS
        self.bgStim = bgStim
        self.fgStim = fgStim
        
        #INITIALIZE TERRAIN
        self.terrain = terrain
        self.offscreen = self.off_screen_distance(45) #constant for now
        self.updateTerrain()
        
        self.ni = True

        #INITIALIZE ENCODER
        try:
            self.encoder = Encoder(self.nidevice,self.encodervinchannel,self.encodervsigchannel)
            self.encoder.start()
            time.sleep(0.1) #wait for first data buffer
            self.encDeg = self.encoder.getDegrees() #get initial state
        except Exception, e:
            print "Could not initialize Encoder.  Ensure that NI is connected properly.", e
            self.encDeg = 0
            self.ni = False
            self.encoder = None
        self.x = 0
        self.lastDx = 0
        self.crossedZero = True
        
        #INITIALIZE REWARD
        try:
            self.reward = Reward(self.nidevice,self.rewardport,self.rewardline)
            self.reward.rewardtime = self.rewardtime
            self.reward.start()
        except Exception, e:
            print "Could not initialize Reward.  Ensure that NI is connected properly."
            self.ni = False
            self.reward = None
        self.framescorrect = 0
        
        #REPLAY MODE? Modify these values after instantiating but before run()
        self.replay = False
        self.saveframes = False
        self.framelist = []
        self.framefolder = r"C:\SavedFrames"
        
        self.replayx = []
        self.replayterrain = []
        self.replaylaps = []
        
        #NO NI BOARD? TURN ON KEYBOARD CONTROL (CHECKING KEYS HURTS PERFORMACE)
        if not self.ni:
            print "Switching to key control..."
            self.keys = key.KeyStateHandler()
            self.window.winHandle.push_handlers(self.keys)

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
        ##TODO: Merge with SweepStim.updateBackground (these do almost the same thing and shouldn't be separate)
        for i in range(len(self.terrain.params)):
            k,v = self.terrain.params[i]['name'],self.terrain.current[i]
            try: #parameter is a proper stimulus property
                execstring = "self.fgStim.set"+ k + "(" + str(v) + ")"
                exec(execstring)
            except Exception, e: #paramter is not a proper stimulus property
                if k == "TF": #special case for temporal freqency
                    self.fgFrame[k] = v
                elif k == "Tex": #special case for textures (fix later)
                    self.fgStim.setTex(v)
                elif k == "Image": #special case for images
                    self.fgStim.setImage(v)
                elif k == "PosX": #special case for x position
                    self.fgStim.setPos((v,self.fgStim.pos[1]))
                elif k == "PosY": #special case for y position
                    self.fgStim.setPos((self.fgStim.pos[0],v))
                else: print "Sweep parameter is incorrectly formatted:", k, v, e
        self.terrainlog.append(self.terrain.current)

                
    def checkEncoder(self):
        """ Checks encoder values and tweaks foreground object position based on speedgain. """
        ##TODO: Function has become too long, does too much.  Should be split.
        if self.ni: 
            deg = self.encoder.getDegrees()
            dx = deg-self.encDeg
            self.encDeg = deg
        else: #NO NI BOARD.  KEY INPUT?
            if self.keys[key.D]:
                dx = 1
            elif self.keys[key.A]:
                dx = -1
            else:
                dx = 0
                
        if 180 > dx > -180: #encoder hasn't looped
            self.x += dx*self.terrain.speedgain
            self.lastDx = dx
        elif dx >= 180: #encoder has looped forward
            self.x += self.lastDx*self.terrain.speedgain
        elif dx <=-180: #encoder has looped backward
            self.x -= 0-self.lastDx*self.terrain.speedgain
        
        #check to see if this is a replay, if so, make changes
        if self.replay:
            if len(self.replayx) > 0: #more frames left
                self.x = self.replayx[0]
                del self.replayx[0]
                if self.replaylaps[0][1]==self.vsynccount: #lap completed
                    self.fgStim.setOri(self.replayterrain[0][0])
                    self.fgStim.setColor(self.replayterrain[0][1])
                    del self.replayterrain[0]
            else: self.cleanup() #no more frames in replay. we're done.                
        
        #check for lap completion
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
        """Gets off screen distance using formula to compensate for orientation of object 
            THIS MIGHT BE UNECESSARY AND COULD BE REMOVED.
        """
        x = misc.deg2pix(self.terrain.objectwidthDeg, self.monitor) # converts width of object to pixels from degrees
        dist = orientation/45*(numpy.sqrt(2*(x)**2)-x) + x #pythagorean theorem
        return dist/2 #float divide by two because measurement is from center of object
        
    def cleanup(self):
        """ Destructor """
        #STOP CLOCKS
        self.window.setRecordFrameIntervals(False) #stop recording frame intervals     
        self.stoptime = time.clock() #TIME SENSITIVE STUFF ENDS HERE
        
        #FLIP FOR SYNC SQUARE CLEAR
        for i in range(30):
            self.window.flip()            
        
        timestr = str(datetime.timedelta(seconds = (self.stoptime-self.starttime)))
        print "Actual experiment duration:", timestr
        self.stopdatetime = datetime.datetime.now()
        #DISPLAY SOME STUFF
        print "Actual sweeps completed:", str(self.sweepsdisplayed)
        self.printFrameInfo()
        #PRINT REWARD COUNT
        print "Rewards dispensed:",len(self.rewards)
        #LOG INFORMATION
        if not self.replay: self.logMeta()
        #CLOSE EVERYTHING
        if self.ni:
            self.encoder.clear()
            self.reward.clear()
        self.window.close()
        sys.exit()
        
    def logMeta(self):
        """ Writes all important information to log. """
        ##TODO: COME UP WITH A PRETTIER, SHORTER WAY TO DO THIS
        dir = self.logdir
        file = self.mouseid + ".log" #logger automatically appends timestamp
        path = os.path.join(dir,file)
        log = ailogger(path)
        log.backupFileDir = self.backupdir
        log.add(script = self.script)
        log.add(scripttext = open(self.script,'r').read())
        log.add(mouseid = self.mouseid)
        log.add(userid = self.userid)
        log.add(task = self.task)
        log.add(stage = self.stage)
        log.add(protocol = self.protocol)
        log.add(monitor = getMonitorInfo(self.monitor))
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
        log.add(runs = self.runs)
        log.add(blanksweeps = self.blanksweeps)
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
        log.add(bgsweepframes = getSweepFrames(self.bgsweeporder,self.sweeplength,self.preexpsec,self.postexpsec,self.postsweepsec))
        log.add(terrain = self.terrain.__dict__)
        log.add(reward = repr(self.reward))
        log.add(encoder = repr(self.encoder))
        log.add(posx = self.posx)
        log.add(dx = map(prettyfloat,self.dx))
        log.add(vsyncintervals = map(prettyfloat,self.intervalsms.tolist()))
        log.add(droppedframes = self.droppedframes)
        log.close()
        
    def flip(self):
        """ Flips display and sets frame bits. """
        self.window.flip() # flips display
        if self.saveframes:
            if self.vsynccount in self.framelist:
                self.window.getMovieFrame()
                filename = os.path.join(self.framefolder,str(self.vsynccount)+'.tif')
                self.window.saveMovieFrames(fileName=filename)

    def check_keys(self):
        """Checks key input"""
        for keys in event.getKeys(timeStamped=True):
            if keys[0]in ['i']:
                    if self.ni: self.reward.reward()
                    self.rewards.append((time.clock(), self.vsynccount))
            elif keys[0]in ['escape','q']:
                self.cleanup()

    def run(self):
        """ Main stimuilus setup and loop """
        #FLIP TO GET READY FOR FIRST FRAME
        for i in range(30):
            self.window.flip()
        
        #PRE EXPERIMENT INFO PRINT
        self.printExpInfo()        
        
        #START CLOCKS
        self.startdatetime = datetime.datetime.now()
        self.starttime = time.clock() #TIME SENSITIVE STUFF STARTS HERE
        self.vsynccount = 0
        
        self.window.setRecordFrameIntervals() #start checking frame intervals
        #PRE EXPERIMENT LOOP
        for vsync in range(int(self.preexpsec*60)):
            self.updateFrame(vsync)
            if self.fgStim is not None: 
                self.checkTerrain()
                self.checkEncoder()
                self.fgStim.setPos([self.x,self.fgStim.pos[1]]) #set fgStim position every frame
                self.fgStim.draw()
            if self.syncsqr: self.flipSyncSqr()
            self.flip()
            self.vsynccount += 1
        
        #SWEEP LOOPS
        for sweep in self.bgsweeporder:
            self.updateBackground(sweep) #update background sweep parameters
            self.updateForeground(sweep) #update foreground sweep parameters (not implemented)
            
            #MAIN DISPLAY LOOP
            for vsync in range(int(self.sweeplength*60)):
                self.updateFrame(vsync)
                if self.bgStim is not None:
                    self.bgStim.draw()
                if self.fgStim is not None: 
                    self.checkTerrain()
                    self.checkEncoder()
                    self.fgStim.setPos([self.x,self.fgStim.pos[1]]) #set fgStim position every frame
                    self.fgStim.draw()
                self.check_keys()
                if self.syncsqr: self.flipSyncSqr()
                self.flip()
                self.vsynccount += 1
            self.sweepsdisplayed += 1
            
            #POST SWEEP DISPLAY LOOP
            for vsync in range(int(self.postsweepsec*60)):
                self.updateFrame(vsync)
                if self.fgStim is not None:
                    self.checkTerrain()
                    self.checkEncoder()
                    self.fgStim.setPos([self.x,self.fgStim.pos[1]])
                    self.fgStim.draw()
                self.check_keys()
                if self.syncsqr: self.flipSyncSqr()
                self.flip()
                self.vsynccount += 1
            
        #POST EXPERIMENT LOOP
        for vsync in range(int(self.postexpsec*60)):
            self.updateFrame(vsync)
            if self.fgStim is not None:
                self.checkTerrain()
                self.checkEncoder()
                self.fgStim.setPos([self.x,self.fgStim.pos[1]])
                self.fgStim.draw()
            if self.syncsqr: self.flipSyncSqr()
            self.flip()
            self.vsynccount += 1    
        
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
    params['backupdir'] = None #backup to network
    params['mouseid'] = "test" #name of the mouse
    params['userid'] = "derricw" #name of the user
    params['task'] = "Virtual Foraging" #task type
    params['stage'] = "Acrylic Wheel" #stage
    params['protocol'] = "" #implemented later
    params['nidevice']='Dev1' #NI device name
    params['rewardline']=0 #NI DO line
    params['rewardport']=1 #NI DO port
    params['encodervinchannel']=1 #NI Vin channel
    params['encodervsigchannel']=2 #NI Vsig channel
    params['blanksweeps']=5 #blank sweep every x sweeps
    params['bgcolor']='gray' #background color
    params['syncsqr']=True
    params['syncsqrloc']=(-600,-350)
    params['script']=__file__
    
    #TERRAIN CREATION AND PARAMETERS (see Terrain for additional parameters)
    terrain = Terrain()
    terrain.params.append({'name':'Color','possible':[-1,1],'correct':[1],'relevance':True})
    terrain.params.append({'name':'Ori','possible':range(0,90,15),'correct':[0],'relevance':True})
    terrain.current = [-1,0] #initial values (order is the order added to params)
    terrain.objectwidthDeg = 10
    terrain.speedgain = 10
    terrain.correctfreq = 0.25
    
    #SET CONSOLE OUTPUT LEVEL, INITIALIZE WINDOWS
    #logging.console.setLevel(logging.DEBUG) #uncommet for diagnostics
    window = visual.Window(units='norm',monitor='testMonitor', fullscr = True, screen = 1, waitBlanking=False)
    window.setColor(params['bgcolor'])
    
    #CREATE BACKGROUND STIMULUS
    
    grating = visual.GratingStim(window,tex="sin",mask="gauss",texRes=64,
           size=[10,10], sf=1, ori = 0, name='grating', autoLog=False, units = 'deg')
           
    #CREATE BACKGROUND FRAME PARAMETERS (what changes between frames and how much)
    bgFrame = {}
    
    #CREATE BACKGROUND SWEEP PARAMETERS (what changes between sweeps, and in what order)
    bgSweep = {}
    
    bgSweep['Ori'] = ([0,45],1)
    bgSweep['SF'] = ([0.5,1],3)
    bgSweep['Contrast'] = ([0.5,1],0)
    bgSweep['TF'] = ([1],2)
    bgSweep['Phase'] = ([0],4)
    
    #CREATE FOREGROUND STIMULUS
    monitor = monitors.Monitor('testMonitor')
    box = visual.GratingStim(window,size = (misc.deg2pix(terrain.objectwidthDeg,monitor), misc.deg2pix(terrain.objectwidthDeg,monitor)), units = 'pix', color = -1, autoLog=False, tex=None)
    #fgrating = visual.GratingStim(window,tex="sin",mask="gauss", texRes=64,size=[20,20],units='deg',sf=2)    
    #img = visual.ImageStim(window, image = "C:\\Users\\derricw\\Pictures\\facepalm.jpg", size = [450,300], units = 'pix', autoLog=False) #creates an image from an image in specified directory
    #CREATE FOREGROUND STIMULUS FRAME PARAMETERS (what changes between frames and how much (BESIDES XPOSITITON WHICH IS AUTOMATIC FOR THIS EXPERIMENT)
    fgFrame = {}
    
    #CREATE FOREGROUND SWEEP PARAMETERS (what changes between sweeps)
    fgSweep = {}

    #CREATE FORAGING CLASS INSTANCE
    g = Foraging(window = window, terrain = terrain, params = params, bgStim = grating, bgFrame = bgFrame, bgSweep = bgSweep, fgStim = box)
    #RUN IT
    g.run()
