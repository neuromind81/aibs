"""Defines the Foraging Sweep Gratings Experiment"""

from __future__ import division

import os
import struct
import time
import datetime
import numpy as np
np.seterr(all='raise') # raise all numpy errors (like 1/0), don't just warn
import pygame
import OpenGL.GL as gl

import pyglet.window
import pyglet.window.key as key
import pyglet.window.mouse as mouse

import VisionEgg as ve
import VisionEgg.Core
from VisionEgg.Gratings import SinGrating2D
from VisionEgg.MoreStimuli import Target2D
from VisionEgg.Textures import Mask2D

import dimstim.Constants as C
from dimstim.Constants import I, SWEEP
import dimstim.Core as Core
from dimstim.Core import sec2intvsync, cycDeg2cycPix, cycSec2cycVsync, deg2pix, toiter, isotime
try:
    from dimstim.Core import DT # only importable if DT board is installed
except ImportError:
    pass
from Experiment_AIBS import Experiment

printer = C.printer # synonym
info = printer.info
warning = printer.warning
printf2log = printer.printf2log


class Grating(Experiment):
    """Grating experiment"""
    def __init__(self, *args, **kwargs):
        super(Grating, self).__init__(*args, **kwargs)
        self.width = deg2pix(self.static.widthDeg) # do this here so it doesn't have to be done repeatedly in self.updateparams()
        self.height = deg2pix(self.static.heightDeg)
        
        self.terrain = self.static.terrain
        
        #square initialization
        self.brightness = self.terrain.color
        
        #set up encoder
        self.static.encoder.start()
        self.encDeg = self.static.encoder.getDegrees()
        self.lastDx = 0
        if self.static.encoder.getVin() < 1:
            print 'Encoder not connected or powered on.'
            
        #set up reward
        self.framescorrect = 0
        self.static.reward.start()
        
        #set up lap and reward logs
        self.laps = []
        self.rewards = []

    def check(self):
        """Check Grating-specific parameters"""
        super(Grating, self).check()
        '''
        if self.dynamic.speedDegSe == None:
            self.dynamic.speedDegSec = 0 # required for self.updateparams()
        if self.dynamic.speedDegSec == 0: # if speed hasn't been set, make sure position has
            assert self.dynamic.xposDeg != None, 'speedDegSec is 0, xposDeg can\'t be set to None'
            assert self.dynamic.yposDeg != None, 'speedDegSec is 0, xposDeg can\'t be set to None'
        else: # if speed has been set, make sure position hasn't
            assert self.dynamic.xposDeg == None, 'speedDegSec is non-zero, xposDeg must be set to None'
            assert self.dynamic.yposDeg == None, 'speedDegSec is non-zero, yposDeg must be set to None'
        '''
    def build(self):
        """Builds the SweepTable and the Header for this Experiment"""
        # Build the sweep table
        self.sweeptable = Core.SweepTable(experiment=self)
        self.st = self.sweeptable.data # synonym, used a lot by Experiment subclasses

        # Do time and space conversions of applicable static and dynamic parameters - or maybe do this in init - is this really necessary, can't it be done on the fly, or would that be too slow? If too slow, write it inline in C and use scipy.weave?
        # Is there a better place to store these, rather than polluting self namespace?
        self.xorig = deg2pix(self.static.xorigDeg) + I.SCREENWIDTH / 2 # do this once, since it's static, save time in main loop
        self.yorig = deg2pix(self.static.yorigDeg) + I.SCREENHEIGHT / 2
        self.y = self.static.ypos
        self.x = self.xorig
        self.offscreen = self.off_screen_distance(self.static.terrain.orientation)

        # Calculate Experiment duration
        self.sec = self.calcduration()
        info('Expected experiment duration: %s' % isotime(self.sec, 6), tolog=False)


    def createstimuli(self):
        """Creates the VisionEgg stimuli objects for this Experiment subclass"""
        super(Grating, self).createstimuli()

        # Create instances of the Mask2D class, one for each diameter
        if self.static.mask:
            print 'Generating masks',
            self.nmasksamples = 512  # number of samples in mask, must be power of 2, quality/performance tradeoff
            self.masks = {} # init a dictionary
            samplesperpix = self.nmasksamples / deg2pix(min(self.static.widthDeg, self.static.heightDeg))
            for diameterDeg in toiter(self.dynamic.diameterDeg):
                radius = deg2pix(diameterDeg / 2) # in pix
                radiusSamples = samplesperpix * radius # in mask samples
                self.masks[diameterDeg] = Mask2D(function=self.static.mask,
                                                 radius_parameter=radiusSamples, # sigma for gaussian, radius for circle, in units of mask samples
                                                 num_samples=(self.nmasksamples, self.nmasksamples)) # size of mask texture data (# of texels)
                print '.',
            print
        else:
            self.masks = None

        self.nsinsamples = 2048 # number of samples of sine f'n, must be power of 2, quality/performance tradeoff
        self.grating = SinGrating2D(position=(self.xorig, self.yorig), # init to orig,
                                    anchor='center',
                                    size=(deg2pix(self.static.heightDeg), deg2pix(self.static.widthDeg)), # VE defines grating ori as direction of motion of grating, but we want it to be the orientation of the grating elements, so add 90 deg (this also makes grating ori def'n correspond to bar ori def'n). This means that width and height have to be swapped
                                    ignore_time=True, # don't use this class' own time f'n
                                    #mask=self.masks.values()[0], # init to a random mask in maskobjects
                                    num_samples=self.nsinsamples,
                                    max_alpha=1.0, # opaque
                                    on=False) # keep it off until first sweep starts
        self.gp = self.grating.parameters
        
        self.target = Target2D(anchor='center',
                               anti_aliasing=False,
                               color=(self.brightness, self.brightness, self.brightness, 1.0))
        self.tp = self.target.parameters
        
        # Update target stimulus with initial values
        self.tp.position = self.x, self.y
        self.tp.size = deg2pix(self.terrain.objectwidthDeg),deg2pix(self.terrain.objectwidthDeg)
        self.tp.orientation = self.terrain.orientation
        
        
        # Set stimuli tuple
        self.stimuli = (self.background, self.grating, self.target) # last entry will be topmost layer in viewport

    def updateparams(self, i):
        """Updates stimulus parameters, given sweep table index i"""
        if i == None: # do a blank sweep
            self.gp.on = False # turn off the grating, leave all other parameters unchanged
            self.postval = C.MAXPOSTABLEINT # posted to DT port to indicate a blank sweep
            self.nvsyncs = sec2intvsync(self.blanksweeps.sec) # this many vsyncs for this sweep
            self.npostvsyncs = 0 # this many post-sweep vsyncs for this sweep, blank sweeps have no post-sweep delay
        else: # not a blank sweep
            self.gp.on = True # ensure grating is on
            self.postval = i # sweep table index will be posted to DT port
            self.nvsyncs = sec2intvsync(self.st.sweepSec[i]) # this many vsyncs for this sweep
            self.npostvsyncs = sec2intvsync(self.st.postsweepSec[i]) # this many post-sweep vsyncs for this sweep

            """Generate phase as a f'n of vsynci for this sweep
            sine grating eq'n used by VE: luminance(x) = 0.5*contrast*sin(2*pi*sfreqCycDeg*x + phaseRad) + ml ...where x is the position in deg along the axis of the sinusoid, and phaseRad = phaseDeg/180*pi. Motion in time is achieved by changing phaseDeg over time. phaseDeg inits to phase0"""
            sfreq = cycDeg2cycPix(self.st.sfreqCycDeg[i]) # convert it just once, reuse it for this sweep
            """phaseoffset is req'd to make phase0 the initial phase at the centre of the grating, instead of at the edge of the grating as VE does. Take the distance from the centre to the edge along the axis of the sinusoid (which in this case is the height), multiply by spatial freq to get numcycles between centre and edge, multiply by 360 deg per cycle to get req'd phaseoffset. THE EXTRA 180 DEG IS NECESSARY FOR SOME REASON, DON'T REALLY UNDERSTAND WHY, BUT IT WORKS!!!"""
            phaseoffset = self.height / 2 * sfreq * 360 + 180
            phasestep = cycSec2cycVsync(self.st.tfreqCycSec[i]) * 360 # delta cycles per vsync, in degrees of sinusoid

            self.phase = -self.st.phase0[i] - phaseoffset - phasestep * np.arange(self.nvsyncs) # array of phases for this sweep. -ve makes the grating move in +ve direction along sinusoidal axis, see sin eq'n above

            # Update grating stimulus
            self.gp.position = self.xorig+deg2pix(self.st.xposDeg[i]), self.yorig+deg2pix(self.st.yposDeg[i])
            self.gp.orientation = self.static.orioff + self.st.ori[i] + 90 # VE defines grating ori as direction of motion of grating, but we want it to be the orientation of the grating elements, so add 90 deg (this also makes grating ori def'n correspond to bar ori def'n). This means that width and height have to be swapped (done at creation of grating)
            if self.masks:
                self.gp.mask = self.masks[self.st.diameterDeg[i]]
            self.gp.spatial_freq = sfreq
            self.gp.pedestal = self.st.ml[i]
            
            if self.st.contrastreverse[i]: 
                contraststep = cycSec2cycVsync(self.st.cfreqCycSec[i])*self.st.contrast[i]*2
                self.contrast =self.st.contrast[i]*np.sin(contraststep * np.arange(self.nvsyncs))
            else: self.gp.contrast = self.st.contrast[i]

            # Update background parameters
            self.bgp.color = self.st.bgbrightness[i], self.st.bgbrightness[i], self.st.bgbrightness[i], 1.0
            
    
    def checkTerrain(self):
        """Checks terrain to see if a reward needs to be given"""
        if self.static.terrain.iscorrect:
            if I.SCREENWIDTH/2 + self.static.terrain.windowwidth > self.x > I.SCREENWIDTH/2-self.static.terrain.windowwidth:
                if self.framescorrect > self.static.terrain.selectiontime:
                    self.static.reward.reward()
                    self.rewards.append(time.clock())
                    self.static.terrain.iscorrect = False
                self.framescorrect += 1
            else:
                self.framescorrect = 0
        
    def updateTerrain(self):
        self.brightness = self.static.terrain.color
        self.offscreen = self.off_screen_distance(self.static.terrain.orientation)
        self.tp.orientation = self.static.terrain.orientation
        self.tp.color = (self.brightness, self.brightness, self.brightness, 1.0)
    
    def checkEncoder(self):
        '''Gets any input that can change terrain'''
        ##TODO: Put this all in Terrain class
        if self.static.encoder.getVin() > 1: #ensure that encoder voltage is on
            deg = self.static.encoder.getDegrees()
            dx = deg-self.encDeg
            self.encDeg = deg
            if 100 > dx > -100:
                self.x += dx*self.terrain.speedgain
                self.lastDx = dx
            elif dx >= 100:
                self.x += self.lastDx*self.terrain.speedgain
            elif dx <=-100:
                self.x -= 0-self.lastDx*self.terrain.speedgain
        
        #prevents object from blinking when the lapdistance is short  
        if self.x > (self.static.terrain.lapdistance + self.offscreen):
            self.static.terrain.new() # gets new object
            self.updateTerrain()
            self.x = 0-self.offscreen
            self.laps.append(time.clock())
        elif self.x < 0-self.offscreen:
            self.x = self.static.terrain.lapdistance + self.offscreen
            #perhaps do something here so that something happens when they go backwards

    def off_screen_distance(self, orientation = 0):
        '''Gets off screen distance using formula to compensate for orientation of object '''
        x = deg2pix(self.static.terrain.objectwidthDeg) # converts width of object to pixels from degrees
        dist = orientation/45*(np.sqrt(2*(x)**2)-x) + x #pythagorean theorem
        return dist/2 #float divide by two because measurement is from center of object

    def main(self):
        """Run the main stimulus loop for this Experiment subclass

        make screen.get_framebuffer_as_array for all Experiment classes more easily
        available from outside of dimstim (for analysis in neuropy) so you can
        grab the frame buffer data at any timepoint (and use for, say, revcorr)

        """
        for ii, i in enumerate(self.sweeptable.i):

            self.updateparams(i)
            
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
                if self.gp.on: # not a blank sweep
                    self.gp.phase_at_t0 = self.phase[vsynci] # update grating phase
                    if self.st.contrastreverse[i]: self.gp.contrast = self.contrast[vsynci] #if phase reversal is on
                self.tp.position = self.x,self.y
                
                self.checkEncoder()
                self.checkTerrain()
                self.updateTerrain()
                
                self.screen.clear()
                self.viewport.draw()
                ve.Core.swap_buffers() # returns immediately
                gl.glFlush() # waits for next vsync pulse from video card
                self.vsynctimer.tick()
                self.nvsyncsdisplayed += 1 # increment

            # Sweep's done, turn off the grating, do the postsweep delay
            self.gp.on = False
            
            self.staticscreen(nvsyncs=self.npostvsyncs)
            
            if self.quit:
                self.ii = ii + 1 - 1 # dec for accurate count of nsweeps successfully displayed
                break # out of sweep loop

        self.ii = ii + 1 # nsweeps successfully displayed
        
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
        
        '''    #something is wonky here idk what.  Throws excepthook error
        if self.paused:
            warning('dimstim was paused at some point')
        if self.quit:
            warning('dimstim was interrupted before completion')
        else:
            info('dimstim completed successfully\n')
            '''
        
        printf2log('SWEEP ORDER: \n' + str(self.sweeptable.i) + '\n')
        printf2log('SWEEP TABLE: \n' + self.sweeptable._pprint(None) + '\n')
        printf2log('\n' + '-'*80 + '\n') # add minuses to end of log to space it out between sessions
        
        self.logmeta()
        
    def logmeta(self):
        """Logs some stuff to C:\MouseData\ """
        meta = ""
        dir = "C:\\MouseData\\" + self.static.mouseid
        if not os.path.exists(dir): os.makedirs(dir)
        filename = self.static.mouseid + "-" + self.startdatetime.strftime('%y%m%d%H%M%S') + ".log"
        path = os.path.join(dir, filename)
        f = open(path, 'w+')
        meta = "Mouse ID: " + self.static.mouseid + "\n" + "Start Time: " + \
            str(self.startdatetime) + "\n" + "Stop Time: " str(self.stopdatetime) + '\n'
        for l in self.laps: meta += str(l) + ','
        meta = meta[:-1] + '\n'
        for r in self.rewards: meta += str(r) + ','
        meta = meta[:-1] + '\n'
        for s in self.sweeptable.i: meta += str(s) + ','
        meta = meta[:-1] + '\n'
        meta += self.sweeptable._pprint(None))
        f.write(meta)
        f.close()
        
    def staticscreen(self, nvsyncs, postval=C.MAXPOSTABLEINT):
        """Display whatever's defined in the viewport on-screen for nvsyncs,
        and posts postval to the port. Adds ticks to self.vsynctimer"""
        #assert nvsyncs >= 1 # nah, let it take nvsyncs=0 and do nothing and return right away
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
            self.screen.clear()
            self.viewport.draw()
            ve.Core.swap_buffers() # returns immediately
            gl.glFlush() # waits for next vsync pulse from video card
            self.vsynctimer.tick()
            vsynci += int(not self.pause) # don't increment if in pause mode
        if I.DTBOARDINSTALLED: DT.clearBits(SWEEP) # be tidy, clear sweep bit low, delay to make sure Surf sees the end of this sweep
