# -*- coding: utf-8 -*-

'''
Created on Oct 18, 2012

@author: derricw
'''
from psychopy import core, visual, event, logging, misc, monitors
import scipy
import numpy
import itertools
import pylab
from aibs.Terrain import Terrain
from aibs.Encoder import Encoder
from aibs.Reward import Reward
import time

class Foraging(object):

    def __init__(self, window, params, terrain = None, bgSweep = None, fgSweep = None, bgStim = None, fgStim = None, fgFrame = None, bgFrame = None):
        """ Constructor.  Builds Foraging experiment and prepares for run() """
        # generic parameters
        self.params = params
        for k,v in self.params.iteritems():
            setattr(self,k,v)
        self.wwidth = window.size[0]
        self.wheight = window.size[1]
        self.monitor = monitors.Monitor('secondMonitor')
        
        # stuff we want to track
        self.sweepsdisplayed = 0
        self.laps = []
        self.rewards = []
        self.posx = []
        self.dx = []
        self.terrainlog = []
        
        # sweep parameters and frame parameters
        self.bgSweep = bgSweep
        self.fgSweep = fgSweep
        self.bgFrame = bgFrame
        self.fgFrame = fgFrame
        
        # build sweep tables
        self.bgsweeptable, self.bgsweeporder, self.bgdimnames = self.buildSweepTable(self.bgSweep)
        
        # stimulus objects
        self.bgStim = bgStim
        self.fgStim = fgStim
        self.fgStim.setPos([0,0])  #or variable?
        
        # initialize terrain
        self.terrain = terrain
        self.offscreen = self.off_screen_distance(self.terrain.orientation)
        self.updateTerrain()
        
        
        # encoder setup ( args should be read from config file)
        self.encoder = Encoder('Dev1',1,2)
        self.encoder.start()
        time.sleep(0.1)
        self.encDeg = self.encoder.getDegrees()
        self.x = 0
        self.lastDx = 0
        self.crossedZero = True
        
        # reward setup
        self.reward = Reward('Dev1',1,0)
        self.reward.start()
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
        
    def updateBackground(self, sweep):
        """ Updates the background stimulus based on its sweep number. """
        if self.bgStim is not None:
            for k,v in zip(self.bgdimnames, self.bgsweeptable[sweep]):
                try: #parameter is a proper stimulus property
                    exec("self.bgStim.set" + k + "(" + str(v) + ")")
                except: #paramter is not a proper stimulus property
                    if k == "TF": #special case for temporal freqency
                        self.bgFrame[k] = v
                    
                
    def updateForeground(self, sweep):
        pass
        
    def updateFrame(self, vsync):
        if self.bgStim is not None:
            for k,v in self.bgFrame.iteritems():
                try: #parameter is a proper stimulus property
                    exec("self.bgStim.set" + k + "(" + str(v) + ")")
                except: #parameter is not a proper stimulus property
                    if k == "TF": #special case for temporal frequency
                        self.bgStim.setPhase(v*vsync/60.0)
        
    def checkTerrain(self):
        if self.terrain.iscorrect:
            if self.terrain.windowwidth > self.x > -self.terrain.windowwidth:
                if self.framescorrect > self.terrain.selectiontime:
                    self.reward.reward()
                    self.rewards.append(time.clock())
                    self.terrain.iscorrect = False
                    print "REWARD"
                self.framescorrect += 1
            else:
                self.framescorrect = 0
                
    def updateTerrain(self):
        """ Updates terrain variables and logs current instance """
        if self.terrain.color == self.terrain.white: 
            self.fgStim.setLineColor('white')
            self.fgStim.setFillColor('white')
        elif self.terrain.color == self.terrain.black:
            self.fgStim.setLineColor('black')
            self.fgStim.setFillColor('black')
        self.offscreen = self.off_screen_distance(self.terrain.orientation)
        self.fgStim.setOri(self.terrain.orientation)
        self.terrainlog.append((self.terrain.orientation, self.terrain.color))
                
    def checkEncoder(self):
        """ Checks encoder values and tweaks foreground object position. """
        if self.encoder.getVin() > 1: #ensure that encoder voltage is on
            deg = self.encoder.getDegrees()
            dx = deg-self.encDeg
            self.encDeg = deg
            if 180 > dx > -180:
                self.x += dx*self.terrain.speedgain
                self.lastDx = dx
            elif dx >= 180:
                self.x += self.lastDx*self.terrain.speedgain
            elif dx <=-180:
                self.x -= 0-self.lastDx*self.terrain.speedgain
        
        #prevents object from blinking when the lapdistance is short
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
        intervalsMS = numpy.array(window.frameIntervals[1:])*1000
        m=pylab.mean(intervalsMS)
        sd=pylab.std(intervalsMS)
        distString= "Mean=%.1fms,    s.d.=%.1f,    99%%CI=%.1f-%.1f" %(m,sd,m-3*sd,m+3*sd)
        nTotal=len(intervalsMS)
        nDropped=sum(intervalsMS>(1.5*m))
        droppedString = "Dropped/Frames = %i/%i = %.3f%%" %(nDropped,nTotal,nDropped/float(nTotal))
        #calculate some values
        print self.vsynccount
        print distString
        print droppedString
        
        
    def cleanup(self):
        """ Destructor """
        self.printFrameInfo()
        self.logMeta()
        self.encoder.clear()
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
            self.vsynccount += 1
            window.flip()
        
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
                    self.fgStim.setPos([self.x,0])
                    
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
    
    # set generic parameters
    params = {}
    params['preexpsec'] = 2
    params['postexpsec'] = 2
    params['sweeplength'] = 2
    params['postsweepsec'] = 1
    params['rewardtime'] = 0.03
    
    # create terrain parameters
    terrain = Terrain(['color','orientation'])
    terrain.objectwidthDeg = 10
    
    # set console outpub, intialize window
    #logging.console.setLevel(logging.DEBUG) #uncommet for diagnostics
    window = visual.Window(units='norm',monitor='testMonitor', fullscr = True, screen = 1)
    
    # create bg stimulus
    grating = visual.GratingStim(window,tex="sin",mask="None",texRes=64,
           size=[60,60], sf=1, ori = 0, name='grating', autoLog=False, units = 'deg')
    # create bg stimulus frame parameters
    bgFrame = {}
    #bgFrame['Phase'] = (0.01,'+') # tfeq = 1 cycles/sec = 360 degrees/sec = 6 degrees/frame
    
    # create bg stimulus sweep parameters (what changes between sweeps)
    bgSweep = {}
    bgSweep['Ori'] = ([0,15,30,45],1)
    bgSweep['SF'] = ([1],3)
    bgSweep['Contrast'] = ([1],0)
    bgSweep['TF'] = ([1],2)
    
    # create fg stimulus 
    sqmatrix = numpy.zeros((64,64))
    monitor = monitors.Monitor('secondMonitor')
    box = visual.Rect(window,width = misc.deg2pix(terrain.objectwidthDeg,monitor), height = misc.deg2pix(terrain.objectwidthDeg,monitor), units = 'pix', fillColor = 'black', lineColor = 'black', autoLog=False)
    
    
    # create fg stimulus frame parameters (what changes between frames and how much)
    
    # create fg stimulus sweep parameters (what changes between sweeps)
    

    
    
    f = Foraging(window = window, terrain = terrain, params = params, bgStim = grating, bgFrame = bgFrame, bgSweep = bgSweep, fgStim = box)
    f.run()
