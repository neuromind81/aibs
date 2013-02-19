# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 20:40:43 2013

@author: derricw
"""
"""To control the screen and visual stimuli for experiments
"""
# Part of the PsychoPy library
# Copyright (C) 2012 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

import sys, os, glob, copy
#on windows try to load avbin now (other libs can interfere)
if sys.platform=='win32':
    #make sure we also check in SysWOW64 if on 64-bit windows
    if 'C:\\Windows\\SysWOW64' not in os.environ['PATH']:
        os.environ['PATH']+=';C:\\Windows\\SysWOW64'
    try:
        from pyglet.media import avbin
        haveAvbin=True
    except ImportError:
        haveAvbin=False#either avbin isn't installed or scipy.stats has been imported (prevents avbin loading)

import psychopy #so we can get the __path__
from psychopy import core, platform_specific, logging, preferences, monitors, event, visual
import psychopy.colors
import psychopy.event
#misc must only be imported *after* event or MovieStim breaks on win32 (JWP has no idea why!)
import psychopy.misc
import Image
import psychopy.makeMovies

if sys.platform=='win32' and not haveAvbin:
    logging.error("""avbin.dll failed to load. Try importing psychopy.visual as the first
    library (before anything that uses scipy) and make sure that avbin is installed.""")

import numpy
from numpy import sin, cos, pi

from psychopy.core import rush

prefs = preferences.Preferences()#load the site/user config files
reportNDroppedFrames=5#stop raising warning after this
reportNImageResizes=5
global _nImageResizes
_nImageResizes=0

#shaders will work but require OpenGL2.0 drivers AND PyOpenGL3.0+
from ctypes import *
import pyglet
pyglet.options['debug_gl'] = False#must be done before importing pyglet.gl or pyglet.window
GL = pyglet.gl

import psychopy.gamma
#import pyglet.gl, pyglet.window, pyglet.image, pyglet.font, pyglet.event
import psychopy._shadersPyglet as _shaders
try:
    from pyglet import media
    havePygletMedia=True
except:
    havePygletMedia=False

try:
    import pygame
    havePygame=True
except:
    havePygame=False

#check for advanced drawing abilities
#actually FBO isn't working yet so disable
try:
    import OpenGL.GL.EXT.framebuffer_object as FB
    #for pyglet these functions are under .gl like everything else
    haveFB=True
except:
    haveFB=False

try:
    from matplotlib import nxutils
    haveNxutils = True
except:
    haveNxutils = False

global DEBUG; DEBUG=False

#symbols for MovieStim
from psychopy.constants import *
#PLAYING=1
#STARTED=1
#PAUSED=2
#NOT_STARTED=0
#FINISHED=-1

#keep track of windows that have been opened
openWindows=[]

class WarpWindow(visual.Window):
    
    """Used to set up a context in which to draw objects,
    using either PyGame (python's SDL binding) or pyglet.

    The pyglet backend allows multiple windows to be created, allows the user to specify
    which screen to use (if more than one is available, duh!) and allows movies to be
    rendered.

    Pygame has fewer bells and whistles, but does seem a little faster in text rendering.
    Pygame is used for all sound production and for monitoring the joystick.

    """
    def __init__(self,
                 size = (800,600),
                 pos = None,
                 color=(0,0,0),
                 colorSpace='rgb',
                 rgb = None,
                 dkl=None,
                 lms=None,
                 fullscr=None,
                 allowGUI=None,
                 monitor=dict([]),
                 bitsMode=None,
                 winType=None,
                 units=None,
                 gamma = None,
                 blendMode='avg',
                 screen=0,
                 viewScale = None,
                 viewPos  = None,
                 viewOri  = 0.0,
                 waitBlanking=True,
                 allowStencil=False,
                 stereo=False,
                 name='window1'):
        """
        :Parameters:

            size : (800,600)
                Size of the window in pixels (X,Y)
            pos : *None* or (x,y)
                Location of the window on the screen
            rgb : [0,0,0]
                Color of background as [r,g,b] list or single value. Each gun can take values betweeen -1 and 1
            fullscr : *None*, True or False
                Better timing can be achieved in full-screen mode
            allowGUI :  *None*, True or False (if None prefs are used)
                If set to False, window will be drawn with no frame and no buttons to close etc...
            winType :  *None*, 'pyglet', 'pygame'
                If None then PsychoPy will revert to user/site preferences
            monitor : *None*, string or a `~psychopy.monitors.Monitor` object
                The monitor to be used during the experiment
            units :  *None*, 'height' (of the window), 'norm' (normalised),'deg','cm','pix'
                Defines the default units of stimuli drawn in the window (can be overridden by each stimulus)
                See :ref:`units` for explanation of options.
            screen : *0*, 1 (or higher if you have many screens)
                Specifies the physical screen that stimuli will appear on (pyglet winType only)
            viewScale : *None* or [x,y]
                Can be used to apply a custom scaling to the current units of the :class:`~psychopy.visual.Window`.
            viewPos : *None*, or [x,y]
                If not None, redefines the origin for the window
            viewOri : *0* or any numeric value
                A single value determining the orientation of the view in degs
            waitBlanking : *None*, True or False.
                After a call to flip() should we wait for the blank before the script continues
            gamma :
                Monitor gamma for linearisation (will use Bits++ if possible). Overrides monitor settings
            bitsMode : None, 'fast', ('slow' mode is deprecated).
                Defines how (and if) the Bits++ box will be used. 'fast' updates every frame by drawing a hidden line on the top of the screen.
            allowStencil : True or *False*
                When set to True, this allows operations that use the OpenGL stencil buffer
                (notably, allowing the class:`~psychopy.visual.Aperture` to be used).
            stereo : True or *False*
                If True and your graphics card supports quad buffers then this will be enabled.
                You can switch between left and right-eye scenes for drawing operations using
                :func:`~psychopy.visual.Window.setBuffer`

            :note: Preferences. Some parameters (e.g. units) can now be given default values in the user/site preferences and these will be used if None is given here. If you do specify a value here it will take precedence over preferences.

        """
        self.name=name
        self.size = numpy.array(size, numpy.int)
        self.pos = pos
        self.winHandle=None#this will get overridden once the window is created

        self._defDepth=0.0
        self._toLog=[]

        #settings for the monitor: local settings (if available) override monitor
        #if we have a monitors.Monitor object (psychopy 0.54 onwards)
        #convert to a Monitor object
        if monitor==None:
            self.monitor = monitors.Monitor('__blank__')
        if type(monitor) in [str, unicode]:
            self.monitor = monitors.Monitor(monitor)
        elif type(monitor)==dict:
            #convert into a monitor object
            self.monitor = monitors.Monitor('temp',currentCalib=monitor,verbose=False)
        else:
            self.monitor = monitor

        #otherwise monitor will just be a dict
        self.scrWidthCM=self.monitor.getWidth()
        self.scrDistCM=self.monitor.getDistance()

        scrSize = self.monitor.getSizePix()
        if scrSize==None:
            self.scrWidthPIX=None
        else:self.scrWidthPIX=scrSize[0]

        if fullscr==None: self._isFullScr = prefs.general['fullscr']
        else: self._isFullScr = fullscr
        if units==None: self.units = prefs.general['units']
        else: self.units = units
        if allowGUI==None: self.allowGUI = prefs.general['allowGUI']
        else: self.allowGUI = allowGUI
        self.screen = screen

        #parameters for transforming the overall view
        #scale
        if type(viewScale) in [list, tuple]:
            self.viewScale = numpy.array(viewScale, numpy.float64)
        elif type(viewScale) in [int, float]:
            self.viewScale = numpy.array([viewScale,viewScale], numpy.float64)
        else: self.viewScale = viewScale
        #pos
        if type(viewPos) in [list, tuple]:
            self.viewPos = numpy.array(viewPos, numpy.float64)
        else: self.viewPos = viewPos
        self.viewOri  = float(viewOri)
        self.stereo = stereo #use quad buffer if requested (and if possible)

        #setup bits++ if possible
        self.bitsMode = bitsMode #could be [None, 'fast', 'slow']
        if self.bitsMode!=None:
            from psychopy.hardware.crs import bits
            self.bits = bits.BitsBox(self)
            self.haveBits = True

        #gamma
        if self.bitsMode!=None and hasattr(self.monitor, 'lineariseLums'):
            #rather than a gamma value we could use bits++ and provide a complete linearised lookup table
            #using monitor.lineariseLums(lumLevels)
            self.gamma=None
        if gamma != None and (type(gamma) in [float, int]):
            #an integer that needs to be an array
            self.gamma=[gamma,gamma,gamma]
            self.useNativeGamma=False
        elif gamma != None:# and (type(gamma) not in [float, int]):
            #an array (hopefully!)
            self.gamma=gamma
            self.useNativeGamma=False
        elif type(self.monitor.getGammaGrid())==numpy.ndarray:
            self.gamma = self.monitor.getGammaGrid()[1:,2]
            if self.monitor.gammaIsDefault(): #are we using the default gamma for all monitors?
                self.useNativeGamma=True
            else:self.useNativeGamma=False
        elif self.monitor.getGamma()!=None:
            self.gamma = self.monitor.getGamma()
            self.useNativeGamma=False
        else:
            self.gamma = None #gamma wasn't set anywhere
            self.useNativeGamma=True

        #load color conversion matrices
        dkl_rgb = self.monitor.getDKL_RGB()
        if dkl_rgb!=None:
            self.dkl_rgb=dkl_rgb
        else: self.dkl_rgb = None
        lms_rgb = self.monitor.getLMS_RGB()
        if lms_rgb!=None:
            self.lms_rgb=lms_rgb
        else: self.lms_rgb = None

        #set screen color
        self.colorSpace=colorSpace
        if rgb!=None:
            logging.warning("Use of rgb arguments to stimuli are deprecated. Please use color and colorSpace args instead")
            self.setColor(rgb, colorSpace='rgb')
        elif dkl!=None:
            logging.warning("Use of dkl arguments to stimuli are deprecated. Please use color and colorSpace args instead")
            self.setColor(dkl, colorSpace='dkl')
        elif lms!=None:
            logging.warning("Use of lms arguments to stimuli are deprecated. Please use color and colorSpace args instead")
            self.setColor(lms, colorSpace='lms')
        else:
            self.setColor(color, colorSpace=colorSpace)

        #check whether FBOs are supported
        if blendMode=='add' and not haveFB:
            logging.warning("""User requested a blendmode of "add" but framebuffer objects not available. You need PyOpenGL3.0+ to use this blend mode""")
            self.blendMode='average' #resort to the simpler blending without float rendering
        else: self.blendMode=blendMode

        self.allowStencil=allowStencil
        #setup context and openGL()
        if winType==None:#choose the default windowing
            self.winType=prefs.general['winType']
        else:
            self.winType = winType
        if self.winType=='pygame' and not havePygame:
            logging.warning("Requested pygame backend but pygame is not installed or not fully working")
            self.winType='pyglet'
        #setup the context
        if self.winType == "pygame": self._setupPygame()
        elif self.winType == "pyglet": self._setupPyglet()

        #check whether shaders are supported
        if self.winType=='pyglet':#we can check using gl_info
            if pyglet.gl.gl_info.get_version()>='2.0':
                self._haveShaders=True #also will need to check for ARB_float extension, but that should be done after context is created
            else:
                self._haveShaders=False
        else:
            self._haveShaders=False

        self._setupGL()
        
        
        
        
        
        self.frameClock = core.Clock()#from psycho/core
        self.frames = 0         #frames since last fps calc
        self.movieFrames=[] #list of captured frames (Image objects)

        self.recordFrameIntervals=False
        self.recordFrameIntervalsJustTurnedOn=False # Allows us to omit the long timegap that follows each time turn it off
        self.nDroppedFrames=0
        self.frameIntervals=[]
        self._toDraw=[]
        self._toDrawDepths=[]
        self._eventDispatchers=[]
        try:
            self.origGammaRamp=psychopy.gamma.getGammaRamp(self.winHandle)
        except:
            self.origGammaRamp=None
        if self.useNativeGamma:
            logging.info('Using gamma table of operating system')
        else:
            logging.info('Using gamma: self.gamma' + str(self.gamma))
            self.setGamma(self.gamma)#using either pygame or bits++
        self.lastFrameT = core.getTime()

        self.waitBlanking = waitBlanking

        self._refreshThreshold=1/1.0#initial val needed by flip()
        self._monitorFrameRate = self._getActualFrameRate()#over several frames with no drawing
        if self._monitorFrameRate != None:
            self._refreshThreshold = (1.0/self._monitorFrameRate)*1.2
        else:
            self._refreshThreshold = (1.0/60)*1.2#guess its a flat panel

        openWindows.append(self)
    
    def flip(self, clearBuffer=True):
        """Flip the front and back buffers after drawing everything for your frame.
        (This replaces the win.update() method, better reflecting what is happening underneath).

        win.flip(clearBuffer=True)#results in a clear screen after flipping
        win.flip(clearBuffer=False)#the screen is not cleared (so represent the previous screen)
        """
        for thisStim in self._toDraw:
            thisStim.draw()

        

        if haveFB:
            #need blit the frambuffer object to the actual back buffer
            
            FB.glBindFramebufferEXT(FB.GL_FRAMEBUFFER_EXT, 0)#unbind the framebuffer as the render target

            #before flipping need to copy the renderBuffer to the frameBuffer
            '''
            GL.glActiveTexture(GL.GL_TEXTURE0)
            GL.glEnable(GL.GL_TEXTURE_2D)
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.frameTexture)
            GL.glBegin( GL.GL_QUADS )
            GL.glTexCoord2f( 0.0, 0.0 ) ; GL.glVertex2f( -1.0,-1.0 )
            GL.glTexCoord2f( 0.0, 1.0 ) ; GL.glVertex2f( -1.0,1.0 )
            GL.glTexCoord2f( 1.0, 1.0 ) ; GL.glVertex2f( 1.0,1.0 )
            GL.glTexCoord2f( 1.0, 0.0 ) ; GL.glVertex2f( 1.0,-1.0 )
            GL.glEnd()
            '''
            GL.glActiveTexture(GL.GL_TEXTURE0)
            GL.glEnable(GL.GL_TEXTURE_2D)
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.frameTexture)
            GL.glBegin( GL.GL_QUADS )
            GL.glTexCoord2f( 0.0, 0.0 ) ; GL.glVertex2f( -1.0,-1.0 )
            GL.glTexCoord2f( 0.0, 1.0 ) ; GL.glVertex2f( -1.0,1.0 )
            GL.glTexCoord2f( 1.0, 1.0 ) ; GL.glVertex2f( 1.0,1.0 )
            GL.glTexCoord2f( 1.0, 0.0 ) ; GL.glVertex2f( 1.0,-1.0 )
            GL.glTexCoord2f( 0.1, 0.1 ) ; GL.glVertex2f( -0.8,-0.9 )
            GL.glTexCoord2f( 0.1, 0.9 ) ; GL.glVertex2f( -0.8,0.8 )
            GL.glTexCoord2f( 0.9, 0.9 ) ; GL.glVertex2f( 0.8,0.8 )
            GL.glTexCoord2f( 0.9, 0.1 ) ; GL.glVertex2f( 0.8,-0.8 )
            GL.glEnd()
            

        if self.winType =="pyglet":
            #make sure this is current context
            self.winHandle.switch_to()

            GL.glTranslatef(0.0,0.0,-5.0)

            for dispatcher in self._eventDispatchers:
                dispatcher._dispatch_events()
            self.winHandle.dispatch_events()#this might need to be done even more often than once per frame?
            pyglet.media.dispatch_events()#for sounds to be processed
            self.winHandle.flip()
            #self.winHandle.clear()
            GL.glLoadIdentity()


        #rescale/reposition view of the window
        if self.viewScale != None:
            GL.glMatrixMode(GL.GL_PROJECTION)
            GL.glLoadIdentity()
            GL.glOrtho(-1,1,-1,1,-1,1)
            GL.glScalef(self.viewScale[0], self.viewScale[1], 1)
        if self.viewPos != None:
            GL.glMatrixMode(GL.GL_MODELVIEW)
#            GL.glLoadIdentity()
            if self.viewScale==None: scale=[1,1]
            else: scale=self.viewScale
            norm_rf_pos_x = self.viewPos[0]/scale[0]
            norm_rf_pos_y = self.viewPos[1]/scale[1]
            GL.glTranslatef( norm_rf_pos_x, norm_rf_pos_y, 0.0)
        if self.viewOri != None:
            GL.glRotatef( self.viewOri, 0.0, 0.0, -1.0)

        if haveFB:
            #set rendering back to the framebuffer object
            FB.glBindFramebufferEXT(FB.GL_FRAMEBUFFER_EXT, self.frameBuffer)

        #reset returned buffer for next frame
        if clearBuffer: GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        else: GL.glClear(GL.GL_DEPTH_BUFFER_BIT)#always clear the depth bit
        self._defDepth=0.0#gets gradually updated through frame

        #waitBlanking
        if self.waitBlanking:
            GL.glBegin(GL.GL_POINTS)
            GL.glColor4f(0,0,0,0)
            if sys.platform=='win32' and self.glVendor.startswith('ati'):
                pass
            else:
                GL.glVertex2i(10,10)#this corrupts text rendering on win with some ATI cards :-(
            GL.glEnd()
            GL.glFinish()

        #get timestamp
        now = logging.defaultClock.getTime()
        if self.recordFrameIntervals:
            self.frames +=1
            deltaT = now - self.lastFrameT
            self.lastFrameT=now
            if self.recordFrameIntervalsJustTurnedOn: #don't do anything
                self.recordFrameIntervalsJustTurnedOn = False
            else: #past the first frame since turned on
              self.frameIntervals.append(deltaT)
              if deltaT > self._refreshThreshold:
                   self.nDroppedFrames+=1
                   if self.nDroppedFrames<reportNDroppedFrames:
                       logging.warning('t of last frame was %.2fms (=1/%i)' %(deltaT*1000, 1/deltaT), t=now)
                   elif self.nDroppedFrames==reportNDroppedFrames:
                       logging.warning("Multiple dropped frames have occurred - I'll stop bothering you about them!")

        #log events
        for logEntry in self._toLog:
            #{'msg':msg,'level':level,'obj':copy.copy(obj)}
            logging.log(msg=logEntry['msg'], level=logEntry['level'], t=now, obj=logEntry['obj'])
        self._toLog = []

        #    If self.waitBlanking is True, then return the time that
        # GL.glFinish() returned, set as the 'now' variable. Otherwise
        # return None as before
        #
        if self.waitBlanking is True:
            return now

    def _setupGL(self):

        #setup screen color
        if self.colorSpace in ['rgb','dkl','lms','hsv']: #these spaces are 0-centred
            desiredRGB = (self.rgb+1)/2.0#RGB in range 0:1 and scaled for contrast
        else:
            desiredRGB = self.rgb/255.0
        GL.glClearColor(desiredRGB[0],desiredRGB[1],desiredRGB[2], 1.0)
        GL.glClearDepth(1.0)

        GL.glViewport(0, 0, int(self.size[0]), int(self.size[1]))

        GL.glMatrixMode(GL.GL_PROJECTION) # Reset The Projection Matrix
        GL.glLoadIdentity()
        GL.gluOrtho2D(-1,1,-1,1)

        GL.glMatrixMode(GL.GL_MODELVIEW)# Reset The Projection Matrix
        GL.glLoadIdentity()

        GL.glDisable(GL.GL_DEPTH_TEST)
        #GL.glEnable(GL.GL_DEPTH_TEST)                   # Enables Depth Testing
        #GL.glDepthFunc(GL.GL_LESS)                      # The Type Of Depth Test To Do
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        GL.glShadeModel(GL.GL_SMOOTH)                   # Color Shading (FLAT or SMOOTH)
        GL.glEnable(GL.GL_POINT_SMOOTH)

        #check for GL_ARB_texture_float (which is needed for shaders to be useful)
        #this needs to be done AFTER the context has been created
        if not GL.gl_info.have_extension('GL_ARB_texture_float'):
            self._haveShaders=False

        if self.winType=='pyglet' and self._haveShaders:
            #we should be able to compile shaders (don't just 'try')
            self._progSignedTexMask = _shaders.compileProgram(_shaders.vertSimple, _shaders.fragSignedColorTexMask)#fragSignedColorTexMask
            self._progSignedTex = _shaders.compileProgram(_shaders.vertSimple, _shaders.fragSignedColorTex)
            self._progSignedTexMask1D = _shaders.compileProgram(_shaders.vertSimple, _shaders.fragSignedColorTexMask1D)
            self._progSignedTexFont = _shaders.compileProgram(_shaders.vertSimple, _shaders.fragSignedColorTexFont)
#       elif self.winType=='pygame':#on PyOpenGL we should try to get an init value
#            from OpenGL.GL.ARB import shader_objects
#            if shader_objects.glInitShaderObjectsARB():
#                self._haveShaders=True
#                self._progSignedTexMask = _shaders.compileProgram(_shaders.vertSimple, _shaders.fragSignedColorTexMask)#fragSignedColorTexMask
#                self._progSignedTex = _shaders.compileProgram(_shaders.vertSimple, _shaders.fragSignedColorTex)
#            else:
#                self._haveShaders=False

        GL.glClear(GL.GL_COLOR_BUFFER_BIT|GL.GL_DEPTH_BUFFER_BIT)

        #identify gfx card vendor
        self.glVendor=GL.gl_info.get_vendor().lower()

        if sys.platform=='darwin':
            platform_specific.syncSwapBuffers(1)

        if haveFB:
            self._setupFrameBuffer()

    def _setupFrameBuffer(self):
        # Setup framebuffer
        self.frameBuffer = FB.glGenFramebuffersEXT(1)

        FB.glBindFramebufferEXT(FB.GL_FRAMEBUFFER_EXT, self.frameBuffer)
        # Setup depthbuffer
        self.depthBuffer = FB.glGenRenderbuffersEXT(1)
        FB.glBindRenderbufferEXT (FB.GL_RENDERBUFFER_EXT,self.depthBuffer)
        FB.glRenderbufferStorageEXT (FB.GL_RENDERBUFFER_EXT, GL.GL_DEPTH_COMPONENT, int(self.size[0]), int(self.size[1]))

        # Create texture to render to
        self.frameTexture = c_uint(0)
        GL.glGenTextures (1, self.frameTexture)
        GL.glBindTexture (GL.GL_TEXTURE_2D, self.frameTexture)
        GL.glTexParameteri (GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri (GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexImage2D (GL.GL_TEXTURE_2D, 0, GL.GL_RGBA32F_ARB, int(self.size[0]), int(self.size[1]), 0,
                         GL.GL_RGBA, GL.GL_FLOAT, None)

        #attach texture to the frame buffer
        FB.glFramebufferTexture2DEXT (FB.GL_FRAMEBUFFER_EXT, GL.GL_COLOR_ATTACHMENT0_EXT,
                                      GL.GL_TEXTURE_2D, self.frameTexture, 0)
        FB.glFramebufferRenderbufferEXT(FB.GL_FRAMEBUFFER_EXT, GL.GL_DEPTH_ATTACHMENT_EXT,
                                        FB.GL_RENDERBUFFER_EXT, self.depthBuffer)

        status = FB.glCheckFramebufferStatusEXT (FB.GL_FRAMEBUFFER_EXT)
        if status != FB.GL_FRAMEBUFFER_COMPLETE_EXT:
            logging.warning("Error in framebuffer activation")
            return
        GL.glDisable(GL.GL_TEXTURE_2D)


if __name__ == "__main__":
    
    
    #!/usr/bin/env python
    from psychopy import visual, logging, event, core
    
    #create a window to draw in
    myWin = WarpWindow((600,600), allowGUI=False, fullscr = True, screen = 1)
    logging.console.setLevel(logging.DEBUG)
    
    #INITIALISE SOME STIMULI
    grating1 = visual.GratingStim(myWin,mask="None",
        color=[1.0,1.0,1.0],opacity=1.0,
        size=(2.0,2.0), sf=(4,0), ori = 0,
        autoLog=False)#this stim changes too much for autologging to be useful
    grating2 = visual.GratingStim(myWin,mask="None",
        color=[1.0,1.0,1.0],opacity=0.5,
        size=(2.0,2.0), sf=(4,0), ori = 90,
        autoLog=False)#this stim changes too much for autologging to be useful
    
    trialClock = core.Clock()
    t = 0
    while t<20:#quits after 20 secs
    
        t=trialClock.getTime()
    
        #grating1.setPhase(1*t)  #drift at 1Hz
        grating1.draw()  #redraw it
    
        #grating2.setPhase(2*t)    #drift at 2Hz
        grating2.draw()  #redraw it
        
        myWin.flip()          #update the screen
    
        #handle key presses each frame
        for keys in event.getKeys():
            if keys in ['escape','q']:
                core.quit()
