"""Defines the Manual Bar Experiment"""

#===============================================================================
# Imports
#===============================================================================
from __future__ import division

import os
import math
import time
import datetime
import numpy as np
np.seterr(all='raise') # raise all numpy errors (like 1/0), don't just warn
import pyglet.window
import pyglet.window.key as key
import pyglet.window.mouse as mouse
import pygame
#import pygame.locals as pl
import OpenGL.GL as gl
import random

import VisionEgg as ve
import VisionEgg.Core
from VisionEgg.MoreStimuli import Target2D
from VisionEgg.Gratings import SinGrating2D
from VisionEgg.Text import Text

import dimstim.Constants as C
from dimstim.Constants import dc, I
import dimstim.Core as Core
from dimstim.Core import sec2intvsync, deg2pix, pix2deg, iterable, isotime, intround, roundec, cycDeg2cycPix, cycSec2cycVsync
from dimstim.Window import Window
from dimstim.Experiment import Experiment, info, printf2log

STATUSBARHEIGHT = 12 # height of upper and lower status bars (pix)

def invramp(gamma):
    """Inverted gamma ramp"""
    ramp = np.arange(256, dtype=np.uint16) / 255 # normalized linear ramp
    ramp = np.power(ramp, 1 / gamma) * 255 # unnormalized inverted gamma ramp
    return np.uint16(np.round(ramp)) # convert back to nearest ints

#------------------------------------------------------------------------------ 
class SessionClock():
    def __init__(self):
        self.t0 = datetime.datetime.now()
    def elapsed(self):
        t1 = datetime.datetime.now()
        e = t1 - self.t0
        return e
    def secondselapsed(self):
        t1 = datetime.datetime.now()
        e = t1 - self.t0
        return e.seconds

#===============================================================================
# Foraging
#===============================================================================
class Foraging(Experiment):
    """Manual bar experiment"""
    def __init__(self, script, params):
        self.script = script.replace('\\', C.SLASH).replace('.pyc', '.py') # Experiment script file name, with stuff cleaned up
        self.script = os.path.splitdrive(self.script)[-1] # strip the drive name from the start
        self.params = params
        self.params.check()
        for paramname, paramval in params.items():
            setattr(self, paramname, paramval) # bind all parameter names to self
        self.flashvsyncs = sec2intvsync(self.flashSec)
        eye = dc.get('Eye', 'open')
        # Init signals
        self.squarelock, self.brightenText = False, False
        self.UP, self.DOWN, self.LEFT, self.RIGHT = False, False, False, False
        self.PLUS, self.MINUS, self.BRLEFT, self.BRRIGHT = False, False, False, False
        self.LEFTBUTTON, self.RIGHTBUTTON, self.SCROLL = False, False, False
        self.eyei = C.EYESTATES.index(eye)
        
        #Set up initial terrain
        self.brightness = self.terrain.color
        self.ori = self.terrain.orientation
        self.laps = []
        
        #Set up initial gratings
        self.gratingWidth = I.SCREENWIDTH*2
        self.gratingHeight = I.SCREENHEIGHT*2
        self.ml = 0.5
        self.snapDeg = 18
        
        #set up encoder
        self.encoder.start()
        self.encDeg = self.encoder.getDegrees()
        self.lastDx = 0
        if self.encoder.getVin() < 1:
            print 'Encoder not connected or powered on.'
        
        #set up reward
        self.reward.start()
        self.framescorrect = 0
        self.rewards = []
        
        #set up session clock
        self.sc = SessionClock()

    def build(self):
        """Builds the SweepTable and the Header, not required for ManBar experiment"""
        pass

    def setgamma(self, gamma):
        """Set VisionEgg's gamma parameter and apply it to pyglet windows"""
        vc = VisionEgg.config
        super(Foraging, self).setgamma(gamma) # Set VisionEgg's gamma parameter
        if gamma:
            ramps = [] # now apply it to our pyglet windows
            for gamma in (vc.VISIONEGG_GAMMA_INVERT_RED,
                          vc.VISIONEGG_GAMMA_INVERT_GREEN,
                          vc.VISIONEGG_GAMMA_INVERT_BLUE):
                ramps.append(invramp(gamma))
            #for win in self.wins:
            #    win.set_gamma_ramps(ramps)
            self.wins[0].set_gamma_ramps(ramps) # only need to do it for the first one

    def createstimuli(self):
        """Creates the VisionEgg stimuli objects for this Experiment"""
        super(Foraging, self).createstimuli()
        self.target = Target2D(anchor='center',
                               anti_aliasing=self.antialiase,
                               color=(self.brightness, self.brightness, self.brightness, 1.0))
        self.tp = self.target.parameters # synonym
        self.nsinsamples = 2048 # number of samples of sine f'n, must be power of 2, quality/performance tradeoff
        self.grating = SinGrating2D(anchor='center',
                                    size=(self.gratingWidth,self.gratingHeight), # VE defines grating ori as direction of motion of grating, but we want it to be the orientation of the grating elements, so add 90 deg (this also makes grating ori def'n correspond to bar ori def'n). This means that width and height have to be swapped
                                    pedestal=self.ml,
                                    ignore_time=True, # don't use this class' own time f'n
                                    num_samples=self.nsinsamples,
                                    max_alpha=1.0,
                                    on = False) # opaque
        self.gp = self.grating.parameters
        self.fixationspot = ve.Core.FixationSpot(anchor='center',
                                                 color=(1.0, 0.0, 0.0, 0.0),
                                                 size=(5, 5),
                                                 on=True)
        self.fp = self.fixationspot.parameters
        self.centerspot = ve.Core.FixationSpot(anchor='center',
                                                 color=(0.0, 1.0, 0.0, 0.0),
                                                 size=(3, 3),
                                                 on=True)
        self.cp = self.centerspot.parameters
        self.windowleft = ve.Core.FixationSpot(anchor='center',
                                                 color=(1.0, 0.0, 0.0, 0.0),
                                                 size=(3, 10),
                                                 on=True)
        self.wlp = self.windowleft.parameters
        self.windowright = ve.Core.FixationSpot(anchor='center',
                                                 color=(1.0, 0.0, 0.0, 0.0),
                                                 size=(3, 10),
                                                 on=True)
        self.wrp = self.windowright.parameters
        self.textbg = Target2D(size=(900, 145),
                            position=(90, 90),
                            anchor='lowerleft',
                            anti_aliasing=self.antialiase,
                            color=(0.0, 0.0, 0.0, 1.0),
                            on = True)
        self.tbgp = self.textbg.parameters
        ##TODO: switch to pyglet.font
        fontname = pygame.font.match_font('lucidaconsole', bold=False, italic=False)
        self.manbartext = Text(position=(100, 100),
                               anchor='lowerleft',
                               color=(0.0, 1.0, 0.0, 1.0),
                               texture_mag_filter=gl.GL_NEAREST,
                               font_name=fontname,
                               font_size=20)
        self.mbtp = self.manbartext.parameters
        self.datatext = Text(position=(100, 150),
                               anchor='lowerleft',
                               color=(0.0, 1.0, 0.0, 1.0),
                               texture_mag_filter=gl.GL_NEAREST,
                               font_name=fontname,
                               font_size=20)
        self.dtp = self.datatext.parameters
        self.timetext = Text(position=(100, 200),
                               anchor='lowerleft',
                               color=(0.0, 1.0, 0.0, 1.0),
                               texture_mag_filter=gl.GL_NEAREST,
                               font_name=fontname,
                               font_size=20)
        self.ttp = self.timetext.parameters

        # last entry will be topmost layer in viewport
        self.basic_stimuli = (self.background, self.grating, self.target)
        self.all_stimuli = (self.background, self.grating, 
                            self.target,
                            self.fixationspot, self.centerspot,
                            self.textbg, self.manbartext, 
                            self.datatext, self.timetext, 
                            self.windowleft, self.windowright)

    def loadManbar(self, n):
        """Load Manbar n setting in dimstim config file and assign it to the current manual bar"""
        mbn = 'Manbar' + str(n)
        self.x = intround(I.SCREENWIDTH / 2) # initial horizontal position
        self.y = self.ypos #allow user to set vertical position
        self.widthDeg = self.terrain.objectwidthDeg #provided by user in script
        self.heightDeg = self.terrain.objectwidthDeg #same DW
        self.offscreen = self.off_screen_distance(self.terrain.orientation)
        self.ori = self.terrain.orientation
        self.fp.position = self.x, self.y # to use later for eye-tracking
        # for grating
        self.gratingori = 0
        self.tfreqCycSec = 1
        self.sfreqCycDeg = 1
        self.phase0 = 0
        self.contrast = 1
        self.sfreqmultiplier = 1.01
        self.tfreqmultiplier = 1.01
        self.contrastmultiplier = 1.01
        

    def saveManbar(self, n):
        """Save the state of the current manual bar as Manbar n in dimstim config file"""
        mbn = 'Manbar' + str(n)
        dc.set(mbn, 'xorigDeg', roundec(pix2deg(self.x - I.SCREENWIDTH / 2), ndec=6))
        dc.set(mbn, 'yorigDeg', roundec(pix2deg(self.y - I.SCREENHEIGHT / 2), ndec=6))
        dc.set(mbn, 'widthDeg', roundec(self.widthDeg, ndec=6))
        dc.set(mbn, 'heightDeg', roundec(self.heightDeg, ndec=6))
        dc.set(mbn, 'orioff', intround(self.ori))
        dc.update()
        self.fp.position = self.x, self.y
        self.brightenText = mbn # brighten the text for feedback

    def get_freq(self):
        """Get grating temporal frequency"""
        if self.gp.on: #only if gratings are turned on
            if self.UP:
                self.tfreqCycSec *= self.tfreqmultiplier
            elif self.DOWN:
                self.tfreqCycSec /= self.tfreqmultiplier
        """Get grating spatial frequency"""
        if self.RIGHT:
            self.sfreqCycDeg *= self.sfreqmultiplier
        elif self.LEFT:
            self.sfreqCycDeg /= self.sfreqmultiplier


    def get_ori(self):
        """Get grating orientation, make scrolling snap to nearest snapDeg ori step"""
        if self.SCROLL:
            mod = self.gratingori % self.snapDeg
            if mod:
                if self.SCROLL > 0: # snap up
                    self.gratingori += -mod + self.SCROLL * self.snapDeg
                else: # snap down
                    self.gratingori -= mod
            else: # snap up or down by a full snapDeg ori step
                self.gratingori += self.SCROLL * self.snapDeg
            self.SCROLL = False
        elif self.LEFTBUTTON:
            self.gratingori += self.orirateDegSec / I.REFRESHRATE
        elif self.RIGHTBUTTON:
            self.gratingori -= self.orirateDegSec / I.REFRESHRATE
        self.gratingori = self.gratingori % 360 # keep it in [0, 360)
        
    def get_contrast(self):
        """Get grating contrast"""
        if self.PLUS:
            self.contrast *= self.contrastmultiplier
        elif self.MINUS:
            self.contrast /= self.contrastmultiplier

    def get_window(self):
        """Get window target size"""
        if self.BRLEFT:
            self.terrain.windowwidth += 1
        elif self.BRRIGHT:
            self.terrain.windowwidth -= 1
        self.terrain.windowwidth = max(self.terrain.windowwidth, 0) # keep it >= 0
        self.terrain.windowwidth = min(self.terrain.windowwidth, I.SCREENWIDTH) # keep it <= screensize

    def cycleEye(self):
        """Cycle the current eye state and save it to dimstim config file"""
        self.eyei = (self.eyei + 1) % len(C.EYESTATES)
        dc.set('Eye', 'open', C.EYESTATES[self.eyei])
        dc.update()
        self.brightenText = 'Eye' # brighten the text for feedback

    def updatestimuli(self):
        """Update stimuli"""
        # Update target params
        width = deg2pix(self.widthDeg) # convenience
        height = deg2pix(self.heightDeg)
        self.tp.position = self.x, self.y
        self.tp.size = width, height # convert to pix
        self.tp.orientation = self.ori
        self.tp.color = (self.brightness, self.brightness, self.brightness, 1.0)
        self.bgp.color = (self.bgbrightness, self.bgbrightness, self.bgbrightness, 1.0)
        self.cp.position = self.x, self.y # update center spot position
        self.wlp.position = I.SCREENWIDTH/2 - self.terrain.windowwidth, self.y #DW
        self.wrp.position = I.SCREENWIDTH/2 + self.terrain.windowwidth, self.y #DW
        
        # Update grating parms if grating is turned on
        if self.gp.on:
            self.gp.position = I.SCREENWIDTH/2,I.SCREENHEIGHT/2
            self.gp.orientation = self.gratingori
            sfreq = cycDeg2cycPix(self.sfreqCycDeg)
            try:
                self.phase
            except AttributeError: # phase hasn't been init'd yet
                """phaseoffset is req'd to make phase0 the initial phase at the centre of the grating, instead of at the edge of the grating as VE does. Take the distance from the centre to the edge along the axis of the sinusoid (which in this case is the height), multiply by spatial freq to get numcycles between centre and edge, multiply by 360 deg per cycle to get req'd phaseoffset. THE EXTRA 180 DEG IS NECESSARY FOR SOME REASON, DON'T REALLY UNDERSTAND WHY, BUT IT WORKS!!!"""
                phaseoffset = self.gratingHeight / 2 * sfreq * 360 + 180
                self.phase = -self.phase0 - phaseoffset
            phasestep = cycSec2cycVsync(self.tfreqCycSec * self.nscreens) * 360 # delta cycles per vsync, in degrees of sinusoid, adjust for buffer flips on multiple screens
            self.phase = self.phase - phasestep # update phase
            self.gp.spatial_freq = sfreq
            self.gp.phase_at_t0 = self.phase
            self.gp.contrast = self.contrast
            self.bgp.color = (self.bgbrightness, self.bgbrightness, self.bgbrightness, 1.0)
            self.cp.position = I.SCREENWIDTH/2, I.SCREENHEIGHT/2 # update center spot position
        
        # Update text params
        self.mbtp.text = 'x, y = (%5.1f, %5.1f) deg  |  size = (%.1f, %.1f) deg  |  ori = %5.1f deg' \
                         % ( pix2deg(self.x - I.SCREENWIDTH / 2), pix2deg(self.y - I.SCREENHEIGHT / 2),
                             self.widthDeg, self.heightDeg, self.ori)
        self.dtp.text = "%i Rewards | %.1f Rewards/minute " \
                        % (self.reward.rewardcount, 
                           self.reward.rewardcount/(self.sc.secondselapsed()+0.001)*60) #reward counter
        self.ttp.text = "Session time : %s" % str(self.sc.elapsed())[:10]  #shows session time
        
        if self.brightenText == 'Manbar0':
            self.mbtp.color = (1.0, 1.0, 0.0, 1.0) # set to yellow
        elif self.brightenText == 'Manbar1':
            self.mbtp.color = (1.0, 0.0, 0.0, 1.0) # set to red
        elif self.brightenText == 'Eye':
            self.stp.color = (1.0, 0.0, 0.0, 1.0) # set to red
        else:
            self.mbtp.color = (0.0, 1.0, 0.0, 1.0) # set it back to green

    def run(self, caption='Manual bar'):
        """Run the experiment"""
        info('Running Experiment script: %s' % self.script)

        # Init OpenGL graphics windows, one window per requested screen
        platform = pyglet.window.get_platform()
        display = platform.get_default_display()
        self.screens = display.get_screens()
        self.screens = self.screens[:self.nscreens] # keep the first nscreens requested
        self.nscreens = len(self.screens) # update
        self.flashvsyncs = intround(self.flashvsyncs / self.nscreens) # normalize by number of screens to flip in each loop in main()
        self.wins = []
        for screeni, screen in enumerate(self.screens):
            # make all screens fullscreen, except for the first (user) screen
            if screeni == 0:
                win = Window(screen=screen, fullscreen=False, frameless=False)
                win.win.set_location((screen.width - win.win.width)//2,
                                     (screen.height - win.win.height)//2)
                win.win.set_caption(caption)
            else:
                win = Window(screen=screen, fullscreen=True)
            win.win.set_exclusive_mouse(False)
            self.wins.append(win)

        self.setgamma(self.params.gamma)

        # Create VisionEgg stimuli objects, defined by each specific subclass of Experiment
        self.createstimuli()

        # Create viewport(s) with varying stimuli
        self.viewports = []
        for wini, win in enumerate(self.wins):
            if wini == 0:
                self.viewports.append(ve.Core.pyglet_Viewport(window=win, stimuli=self.all_stimuli))
            else:
                self.viewports.append(ve.Core.pyglet_Viewport(window=win, stimuli=self.basic_stimuli))
        self.loadManbar(0) # load settings from Manbar0
        self.bgp.color = self.bgbrightness, self.bgbrightness, self.bgbrightness, 1.0

        # Create the VsyncTimer
        self.vsynctimer = Core.VsyncTimer()
        '''
        # Hack to fix pygame jumping mouse bug in fullscreen mode
        # mousemotion event happens on startup, and then once more due to bug
        for i in range(2):
            pygame.event.peek(pl.MOUSEMOTION)
        pygame.mouse.set_pos(self.x, I.SCREENHEIGHT - 1 - self.y) # set that sucker
        '''
        self.attach_handlers()

        self.nvsyncsdisplayed = 0 # nvsyncs seen by Surf

        self.startdatetime = datetime.datetime.now()
        self.starttime = time.clock() # precision timestamp

        # Run the main stimulus loop, defined by each specific subclass of Experiment
        self.main()

        self.stoptime = time.clock() # precision timestamp
        self.stopdatetime = datetime.datetime.now()

        # Close OpenGL graphics windows (necessary when running from Python interpreter)
        self.wins[0].restore_gamma_ramps() # only needs to be done once
        for win in self.wins:
            win.close()

        #Turn off rotary encoder
        self.encoder.clear()
        
        #Turn off reward
        self.reward.stop()
        self.reward.clear()

        # Print messages to VisionEgg log and to screen
        info(self.vsynctimer.pprint(), toscreen=self.printhistogram, tolog=self.printhistogram)
        info('%d vsyncs displayed' % self.nvsyncsdisplayed)
        info('Experiment duration: %s' % isotime(self.stoptime-self.starttime, 6))
        printf2log('\n' + '-'*80 + '\n') # add minuses to end of log to space it out between sessions
        
        self.logmeta()

    def logmeta(self):
        """Logs some stuff to C:\MouseData\ """
        meta = ""
        dir = "C:\\MouseData\\" + self.mouseid
        if not os.path.exists(dir): os.makedirs(dir)
        filename = self.mouseid + "-" + self.startdatetime.strftime('%y%m%d%H%M%S') + ".log"
        path = os.path.join(dir, filename)
        f = open(path, 'w+')
        meta = "Mouse ID: " + self.mouseid + "\nStart Time: " + \
            str(self.startdatetime) + "\nStop Time: " + str(self.stopdatetime) + '\nLaps: '
        for l in self.laps: meta += str(l) + ','
        meta = meta[:-1] + '\nRewards: '
        for r in self.rewards: meta += str(r) + ','
        meta = meta[:-1] + '\n'
        f.write(meta)
        f.close()        

    def on_mouse_motion(self, x, y, dx, dy):
        """Update target position""" #Turned off (no mouse control in foraging)
        pass


    def on_key_press(self, symbol, modifiers):
        if symbol == key.UP:
            self.UP = True
        elif symbol == key.DOWN:
            self.DOWN = True
        elif symbol == key.RIGHT:
            self.RIGHT = True
        elif symbol == key.LEFT:
            self.LEFT = True
        elif symbol == key.EQUAL:
            self.PLUS = True
        elif symbol == key.MINUS:
            self.MINUS = True
        elif symbol == key.BRACKETLEFT:
            self.BRLEFT = True
        elif symbol == key.BRACKETRIGHT:
            self.BRRIGHT = True
        elif symbol in [key.LSHIFT, key.RSHIFT]:
            self.squarelock = True
        elif symbol == key.I: # on release will dispense a reward
            pass #DW
        elif symbol in [key._0, key.NUM_0]: # set pos and ori to 0
            self.x = I.SCREENWIDTH / 2
            self.y = I.SCREENHEIGHT / 2
            self.ori = 0
        elif symbol in [key.SPACE, key.ENTER, key.NUM_ENTER] or modifiers & key.MOD_CTRL and symbol in [key._1, key.NUM_1]:
            self.saveManbar(0) # save Manbar state 0
        elif modifiers & key.MOD_CTRL and symbol in [key._2, key.NUM_2]:
            self.saveManbar(1) # save Manbar state 1
        elif symbol == key.E:
            self.cycleEye() # cycle eye state
        elif not modifiers & key.MOD_CTRL and symbol in [key._1, key.NUM_1]:
            self.loadManbar(0) # load Manbar state 0
        elif not modifiers & key.MOD_CTRL and symbol in [key._2, key.NUM_2]:
            self.loadManbar(1) # load Manbar state 1

    def on_key_release(self, symbol, modifiers):
        if symbol == key.UP:
            self.UP = False
        elif symbol == key.DOWN:
            self.DOWN = False
        elif symbol == key.RIGHT:
            self.RIGHT = False
        elif symbol == key.LEFT:
            self.LEFT = False
        elif symbol == key.EQUAL:
            self.PLUS = False
        elif symbol == key.MINUS:
            self.MINUS = False
        elif symbol == key.I: #DW
            self.reward.reward() #DW
        elif symbol == key.U:
            self.gp.on = not self.gp.on
        elif symbol == key.BRACKETLEFT:
            self.BRLEFT = False
        elif symbol == key.BRACKETRIGHT:
            self.BRRIGHT = False
        elif symbol in [key.LSHIFT, key.RSHIFT]:
            self.squarelock = False
        elif symbol in [key.SPACE, key.ENTER, key.NUM_ENTER, key.E] or \
            modifiers & key.MOD_CTRL and symbol in [key._1, key.NUM_1, key._2, key.NUM_2]:
            self.brightenText = False

    def on_mouse_press(self, x, y, button, modifiers):
        pass
        

    def on_mouse_release(self, x, y, button, modifiers):
        pass


    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.SCROLL = scroll_y / abs(scroll_y) # +ve or -ve scroll click for grating orientation

    def attach_handlers(self):
        for win in self.wins:
            win.win.push_handlers(self.on_mouse_motion)
            win.win.push_handlers(self.on_key_press)
            win.win.push_handlers(self.on_key_release)
            win.win.push_handlers(self.on_mouse_press)
            win.win.push_handlers(self.on_mouse_release)
            win.win.push_handlers(self.on_mouse_scroll)


    def check_input(self): #can be any type of input, we check an analog encoder
        '''Gets any input that can change terrain besides key input'''
        ##TODO: Put this all in Terrain class
        if self.encoder.getVin() > 1: #ensure that encoder voltage is on
            deg = self.encoder.getDegrees()
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
        if self.x > (self.terrain.lapdistance + self.offscreen):
            self.terrain.new() # gets new object
            self.ori = self.terrain.orientation
            self.brightness = self.terrain.color
            self.offscreen = self.off_screen_distance(self.terrain.orientation)
            self.x = 0-self.offscreen
            self.laps.append(time.clock())
        elif self.x < 0-self.offscreen:
            self.x = self.terrain.lapdistance + self.offscreen
            #perhaps do something here so that something happens when they go backwards
        
    def off_screen_distance(self, orientation = 0):
        '''Gets off screen distance using formula to compensate for orientation of object '''
        x = deg2pix(self.widthDeg) # converts width of object to pixels from degrees
        dist = orientation/45*(np.sqrt(2*(x)**2)-x) + x #pythagorean theorem
        return dist/2 #float divide by two because measurement is from center of object
        
    def check_terrain(self):
        '''Gets any terrain that can change per lap'''
        if self.terrain.iscorrect:
            if I.SCREENWIDTH/2 + self.terrain.windowwidth > self.x > I.SCREENWIDTH/2-self.terrain.windowwidth:
                self.wlp.color = (0.0,1.0,0.0,0.0)
                self.wrp.color = (0.0,1.0,0.0,0.0)
                if self.framescorrect > self.terrain.selectiontime:
                    self.reward.reward()
                    self.terrain.iscorrect = False
                    self.rewards.append(time.clock())
                self.framescorrect += 1
            else:
                self.framescorrect = 0
                self.wlp.color = (1.0,0.0,0.0,0.0)
                self.wrp.color = (1.0,0.0,0.0,0.0)
        else:
            self.wlp.color = (1.0,0.0,0.0,0.0)
            self.wrp.color = (1.0,0.0,0.0,0.0)

    def main(self):
        """Run the main stimulus loop"""
        while np.alltrue([ not win.win.has_exit for win in self.wins ]):

            for win in self.wins:
                win.dispatch_events() # to the event handlers
            
            if self.gp.on:
                self.get_freq()
                self.get_ori()
                self.get_contrast()
            self.get_window() #DW
            self.check_input() #DW
            self.check_terrain()
            self.updatestimuli()

            for win, viewport in zip(self.wins, self.viewports):
                win.switch_to()
                win.clear()
                viewport.draw()
                #ve.Core.swap_buffers() # returns immediately
                win.flip()
                gl.glFlush() # waits for next vsync pulse from video card

            if self.printhistogram: self.vsynctimer.tick()
            self.nvsyncsdisplayed += 1 # increment
