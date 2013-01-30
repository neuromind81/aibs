# -*- coding: utf-8 -*-

'''
Created on Oct 18, 2012

@author: derricw
'''
from psychopy import core, visual, event, logging
import scipy
import numpy
import itertools

class Foraging(object):

    def __init__(self, window, params, terrain = None, bgSweep = None, fgSweep = None, bgStim = None, fgStim = None, fgFrame = None, bgFrame = None):
        
        # generic parameters
        self.params = params
        for k,v in self.params.iteritems():
            setattr(self,k,v)
        
        # sweep parameters and frame parameters
        self.bgSweep = bgSweep
        self.fgSweep = fgSweep
        self.fgFrame = fgFrame
        self.fgFrame = fgFrame
        
        # build sweep tables
        self.sweepcount = 1
        self.dimensions = len(self.bgSweep)
        self.dimarray = []
        self.dimnames = []
        
        for key,values in self.bgSweep.iteritems():
            self.sweepcount *= len(values[0]) # get number of sweeps
        
        for d in range(self.dimensions):
            for k,v in self.bgSweep.iteritems():
                if v[1] == d:
                    self.dimarray.append(len(v[0])) # get ordered dimenstion array
                    self.dimnames.append(k) # get ordered name array
        self.dimlist = [self.bgSweep[k][0] for k in self.dimnames] # get ordered value array
        
        self.sweeptable = list(itertools.product(*self.dimlist)) # get full ordered table
        
        self.sweeporder = range(self.sweepcount)
        
        print self.sweeptable
        print self.sweeporder
        
        # stimulus objects
        self.bgStim = bgStim
        self.fgStim = fgStim
        
        # terrain
        self.terrain = terrain
        
        # stuff we want to track
        self.sweepsdisplayed = 0

    def run(self):
        """ Main loop """
        # repeat drawing for each frame
        trialClock = core.Clock()
        
        # spin for pre-exp period
        while trialClock.getTime() < self.preexpsec:
            window.flip()
        
        
        # start checking frame intervals
        window.setRecordFrameIntervals()
        for sweep in self.sweeporder:
            if not self.bgStim == None:
                for k,v in zip(self.dimnames, self.sweeptable[sweep]):
                    string = "self.bgStim.set" + k + "(" + str(v) + ")"
                    exec(string)
                
            trialClock.reset()
            while trialClock.getTime() < self.sweeplength:
                if not self.bgStim == None:
                    self.bgStim.draw()
                    self.bgStim.setPhase(0.01,'+') #set frame changes
                #handle key presses each frame
                if not self.fgStim == None:
                    self.fgStim.draw()
                for keys in event.getKeys(timeStamped=True):
                    if keys[0]in ['escape','q']:
                        window.close()
                        core.quit()
                window.flip()
            
            
            
if __name__ == "__main__":
    
    params = {}
    params['preexpsec'] = 2
    params['sweeplength'] = 2
    
    # set console outpub, intialize window
    #logging.console.setLevel(logging.DEBUG) #uncommet for diagnostics
    window = visual.Window(units='norm',monitor='testMonitor', fullscr = True)
    
    # create bg stimulus
    grating = visual.GratingStim(window,tex="sin",mask="None",texRes=512,
           size=[60,60], sf=[4,1], ori = 0, name='grating', autoLog=False, units = 'deg')
    # create bg stimulus frame parameters
    bgFrame = {}
    bgFrame['Phase'] = (0.01,'+')
    
    # create bg stimulus sweep parameters (what changes between sweeps)
    bgSweep = {}
    bgSweep['Ori'] = ([0,15,30,45,60,90],1)
    bgSweep['SF'] = ([1,2,3],0)
    bgSweep['Contrast'] = ([0.1,0.5,1],2)
    # create fg stimulus 
    sqmatrix = numpy.zeros((64,64))
    box = visual.Rect(window,width = 15, height = 15, units = 'deg', fillColor = 'black')
    
    
    # create fg stimulus frame parameters (what changes between frames and how much)
    
    # create fg stimulus sweep parameters (what changes between sweeps)
    
    f = Foraging(window = window, params = params, bgStim = grating, bgFrame = bgFrame, bgSweep = bgSweep, fgStim = box)
    f.run()
