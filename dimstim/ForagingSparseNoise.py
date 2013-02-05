"""Defines the SparseNoise Foraging Experiment"""

from __future__ import division

import math
import datetime
import time
import os
from math import pi
import numpy as np
np.seterr(all='raise') # raise all numpy errors (like 1/0), don't just warn
import pygame
import OpenGL.GL as gl

import VisionEgg as ve
import VisionEgg.Core
from VisionEgg.MoreStimuli import Target2D

import dimstim.Constants as C
from dimstim.Constants import I, SWEEP
import dimstim.Core as Core
from dimstim.Core import sec2intvsync, degSec2pixVsync, deg2pix, isotime
try:
    from dimstim.Core import DT # only importable if DT board is installed
except ImportError:
    pass
from aibs.Experiment_AIBS import Experiment
from aibs.ailogger import ailogger, npdict2listdict

printer = C.printer # synonym
info = printer.info
warning = printer.warning
printf2log = printer.printf2log


class ForagingSparseNoise(Experiment):
    """Sparse noise experiment"""
    
    def __init__(self, *args, **kwargs):
        super(ForagingSparseNoise, self).__init__(*args, **kwargs)
        
        self.terrain = self.static.terrain
        
        #square initialization
        self.brightness = self.terrain.color
        
        #set up encoder
        self.static.encoder.start()
        self.lastDx = 0
        if self.static.encoder.getVin() < 1:
            print 'Encoder not connected or powered on.'
            
        #set up reward
        self.framescorrect = 0
        self.static.reward.start()
        
        #set up data logs
        self.laps = []
        self.rewards = []
        self.posx = []
        self.dx = []
        self.terrainlog = []
        
    
    def check(self):
        """Check SparseNoise-specific parameters"""
        super(ForagingSparseNoise, self).check()

        # need to ensure all oris are +ve and < 360. Enforce this during self.check()? or, do mod 360 on all oris, like in manbar. Shouldn't this be done for all stimuli with an ori parameter????????????

        for xi in self.dynamic.xi:
            assert xi in range(self.static.ncellswide)
        for yi in self.dynamic.yi:
            assert xi in range(self.static.ncellshigh)

    def build(self):
        """Builds the SweepTable and the Header for this Experiment"""
        self.sweeptable = Core.SweepTable(experiment=self)
        self.st = self.sweeptable.data # synonym, used a lot by Experiment subclasses

        self.barWidth = deg2pix(self.static.widthDeg / self.static.ncellswide) # in pix
        self.barHeight = deg2pix(self.static.heightDeg / self.static.ncellshigh) # in pix

        self.xi0 = (self.static.ncellswide - 1) / 2 # center of grid, in units of 0-based cell index
        self.yi0 = (self.static.ncellshigh - 1) / 2
        
        self.sec = self.calcduration()
        
        self.xorig = deg2pix(self.static.xorigDeg) + I.SCREENWIDTH / 2 # do this once, since it's static, save time in main loop
        self.yorig = deg2pix(self.static.yorigDeg) + I.SCREENHEIGHT / 2
        
        self.y = self.static.ypos
        self.x = self.xorig

    def createstimuli(self):
        """Creates the VisionEgg stimuli objects for this Experiment subclass"""
        super(ForagingSparseNoise, self).createstimuli()
        self.target = Target2D(anchor='center', on=False) # keep it off until first sweep starts
        
        if self.static.syncsq:
            self.sync = Target2D(anchor='center',
                                   anti_aliasing=False,
                                   color=(0.0, 0.0, 0.0, 1.0),
                                   position = self.static.syncsqloc,
                                   on = True,
                                   size = (100,100))
            self.sp = self.sync.parameters

        if self.static.syncsq:
            self.stimuli = (self.background, self.target, self.sync) # last entry will be topmost layer in viewport
        else:
            self.stimuli = (self.background, self.target) # last entry will be topmost layer in viewport

        self.tp = self.target.parameters # synonym
        self.tp.size = self.barWidth, self.barHeight # static, only needs to be done once


    def updateparams(self, i):
        """Updates stimulus parameters, given sweep table index i"""
        if i == None: # do a blank sweep
            self.tp.on = False # turn off the target, leave all other parameters unchanged
            self.postval = C.MAXPOSTABLEINT # posted to DT port to indicate a blank sweep
            self.nvsyncs = sec2intvsync(self.blanksweeps.sec) # this many vsyncs for this sweep
            self.npostvsyncs = 0 # this many post-sweep vsyncs for this sweep, blank sweeps have no post-sweep delay
        else: # not a blank sweep
            self.tp.on = True # ensure stimulus is on
            self.postval = i # sweep table index will be posted to DT port
            self.nvsyncs = sec2intvsync(self.st.sweepSec[i]) # this many vsyncs for this sweep
            self.npostvsyncs = sec2intvsync(self.st.postsweepSec[i]) # this many post-sweep vsyncs for this sweep

            # Update target position
            ori = self.static.orioff + self.st.ori[i]
            theta = ori / 180 * pi

            dxi = self.st.xi[i] - self.xi0 # destination index - origin index
            dyi = self.st.yi[i] - self.yi0
            sintheta = math.sin(theta)
            costheta = math.cos(theta)
            dx = dxi*self.barWidth*costheta - dyi*self.barHeight*sintheta # see SparseNoise.png for the trigonometry
            dy = dxi*self.barWidth*sintheta + dyi*self.barHeight*costheta

            x = self.xorig + deg2pix(self.st.xposDeg[i]) + dx
            y = self.yorig + deg2pix(self.st.yposDeg[i]) + dy
            self.tp.position = (x, y)

            # Update non-positional target parameters
            self.tp.orientation = ori
            self.tp.color = self.st.brightness[i], self.st.brightness[i], self.st.brightness[i], 1.0
            self.tp.anti_aliasing = self.st.antialiase[i]

            # Update background parameters
            self.bgp.color = self.st.bgbrightness[i], self.st.bgbrightness[i], self.st.bgbrightness[i], 1.0

    def main(self):
        """Run the main stimulus loop for this Experiment subclass

        make screen.get_framebuffer_as_array for all Experiment classes more easily
        available from outside of dimstim (for analysis in neuropy) so you can
        grab the frame buffer data at any timepoint (and use for, say, revcorr)

        """
        for ii, i in enumerate(self.sweeptable.i):

            self.updateparams(i)

            # Set sweep bit high, do the sweep
            for vsynci in xrange(self.nvsyncs): # nvsyncs depends on if this is a blank sweep or not
                for event in pygame.event.get(): # for all events in the event queue
                    if event.type == pygame.locals.KEYDOWN:
                        if event.key == pygame.locals.K_ESCAPE:
                            self.quit = True
                        if event.key == pygame.locals.K_PAUSE:
                            self.pause = not self.pause # toggle pause
                            self.paused = True # remember that a pause happened
                if self.quit:
                    break # out of vsync loop
                
                if self.static.syncsq:
                    if self.sp.color == (1.0,1.0,1.0,1.0): 
                        self.sp.color = (0.0,0.0,0.0,1.0)
                    else: 
                        self.sp.color = (1.0,1.0,1.0,1.0)
                
                self.screen.clear()
                self.viewport.draw()
                ve.Core.swap_buffers() # returns immediately
                gl.glFlush() # waits for next vsync pulse from video card
                self.vsynctimer.tick()
                self.nvsyncsdisplayed += 1 # increment

            # Sweep's done, turn off the target, do the postsweep delay, clear sweep bit low
            self.tp.on = False
            self.staticscreen(nvsyncs=self.npostvsyncs) # clears sweep bit low when done


            if self.quit:
                self.ii = ii + 1 - 1 # dec for accurate count of nsweeps successfully displayed
                break # out of sweep loop

        self.ii = ii + 1 # nsweeps successfully displayed

    def staticscreen(self, nvsyncs, postval=C.MAXPOSTABLEINT):
        """Display whatever's defined in the viewport on-screen for nvsyncs,
        and posts postval to the port. Adds ticks to self.vsynctimer"""

        vsynci = 0

        if self.pause and nvsyncs == 0:
            nvsyncs = 1 # need at least one vsync to get into the while loop and pause the stimulus indefinitely
        while vsynci < nvsyncs: # need a while loop for pause to work
            for event in pygame.event.get(): # for all events in the event queue
                if event.type == pygame.locals.KEYDOWN:
                    if event.key == pygame.locals.K_ESCAPE:
                        self.quit = True
                    if event.key == pygame.locals.K_PAUSE:
                        self.pause = not self.pause # toggle pause
                        self.paused = True
            if self.quit:
                break # out of vsync loop
            if self.pause: # indicate pause to Surf
                pass
            else: # post value to port
                self.nvsyncsdisplayed += 1 # increment. Count this as a vsync that Surf has seen

            if self.static.syncsq:
                if self.sp.color == (1.0,1.0,1.0,1.0): 
                    self.sp.color = (0.0,0.0,0.0,1.0)
                else: 
                    self.sp.color = (1.0,1.0,1.0,1.0)

            self.screen.clear()
            self.viewport.draw()
            ve.Core.swap_buffers() # returns immediately
            gl.glFlush() # waits for next vsync pulse from video card
            self.vsynctimer.tick()
            vsynci += int(not self.pause) # don't increment if in pause mode
        
         
    def run(self):
        """Run the experiment"""

        # Check it first
        self.check()

        info('Running Experiment script: %s' % self.script)

        # Build the SweepTable and the Header
        self.build()

        self.setgamma(self.static.gamma)

        # Init OpenGL graphics screen
        self.screen = ve.Core.get_default_screen()

        # Create VisionEgg stimuli objects, defined by each specific subclass of Experiment
        self.createstimuli()

        # Create a VisionEgg Viewport
        self.viewport = ve.Core.Viewport(screen=self.screen, stimuli=self.stimuli)

        self.initbackgroundcolor()

        self.fix1stsweeplag() # 1st sweep lag hacks

        # Create the VsyncTimer
        self.vsynctimer = Core.VsyncTimer()
        
        self.quit = False # init quit signal
        self.pause = False # init pause signal
        self.paused = False # remembers whether this experiment has been paused
        self.nvsyncsdisplayed = 0 # nvsyncs seen by Surf

        # time-critical stuff starts here
        self.sync2vsync(nswaps=2) # sync up to vsync signal, ensures that all following swap_buffers+glFlush call pairs return on the vsync

        self.startdatetime = datetime.datetime.now()
        self.starttime = time.clock() # precision timestamp

        # Do pre-experiment delay
        self.staticscreen(nvsyncs=sec2intvsync(self.static.preexpSec))

        # Run the main stimulus loop, defined by each specific subclass of Experiment
        self.main()

        # Do post-experiment delay
        self.staticscreen(nvsyncs=sec2intvsync(self.static.postexpSec))

        self.stoptime = time.clock() # precision timestamp
        self.stopdatetime = datetime.datetime.now()
        # time-critical stuff ends here
        
        # Close OpenGL graphics screen (necessary when running from Python interpreter)
        self.screen.close()

        # Print messages to VisionEgg log and to screen
        info(self.vsynctimer.pprint())
        info('%d vsyncs displayed, %d sweeps completed' % (self.nvsyncsdisplayed, self.ii))
        info('Experiment duration: %s expected, %s actual' % (isotime(self.sec, 6), isotime(self.stoptime-self.starttime, 6)))
        
        print "Logging Data..."
        self.logmeta()
        print "Logging Completed."
            
    def logmeta(self):
        """Logs everything important to C:\MouseData\ """
        dir = "C:\\MouseData\\" + self.static.mouseid + "\\"
        file = "sweep.log" #also appends timestamp to 
        path = os.path.join(dir, file)
        log = ailogger(path)
        log.add(script = self.script)
        log.add(starttime = self.startdatetime)
        log.add(stoptime = self.stopdatetime)
        log.comment(' Parameters ')
        log.add(staticparams = self.static)
        log.add(dynamicparams = self.dynamic)
        
        #log.add(variables = self.variables)  #needs _repr_ methon in Core.Variables class
        log.add(sweeporder = self.sweeptable.i.tolist())
        log.add(sweeptable = npdict2listdict(self.sweeptable.data))
        log.add(sweeptableformatted = self.sweeptable._pprint())
        log.comment( ' Mouse Performance Data ')
        log.add(laps = self.laps)
        log.add(rewards = self.rewards)
        log.add(posx = self.posx)
        log.add(dx = self.dx)
        log.add(terrain = self.terrain.__dict__)
        log.add(terrainlog = self.terrainlog)
        log.comment( ' Dimstim Performance Data ')
        log.add(vsynctable = self.vsynctimer.pprint())
        log.add(vsyncsdisplayed = self.nvsyncsdisplayed)
        log.add(sweepscompleted = self.ii)
        log.add(droppedframes = self.vsynctimer.drops)
        log.close()