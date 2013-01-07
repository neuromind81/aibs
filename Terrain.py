'''
Created on Nov 9, 2012

@author: derricw


terrain.py

This is a terrain object made to store parameters for color and orientation training.

It currently only supports "color" and/or "orientation" training.  It should be expanded to accept
    an N-Dimentional array of training names as an argument instead, thus allowing it to be used
    for a large variety of virtual learning tasks.
#------------------------------------------------------------------------------ 

#Example use:


from Terrain import Terrain

t = Terrain(["color"])    #construct a new object
t.color = t.black         #starting color
t.colorcorrect = t.white  #correct color
t.correctfreq = 0.1       #frequency that correct color is shown
t.lapdistance = 2500      #distance in pixels between objects
t.windowwidth = 300       #space (pixels) where objects need to be held to grant a reward
t.selectiontime = 30      #time  (frames) that objects need to be held to grand a reward

t.new()                   #get new random object from parameter arrays

#------------------------------------------------------------------------------ 

'''
import random
import time

#===============================================================================
# Terrain
#===============================================================================

class Terrain(object):
    """Terrain Setup"""
    def __init__(self, training = ["color", "orientation"]):
        """Initializes defaults.  All can be adjusted after construction."""
        self.training = training
        
        #set up color states
        self.black = 0
        self.white = 1
        self.color = self.black # default color state
        
        #set up orientation states
        self.orientation = 45 #starting orientation
        self.oriarray = [0,45,90]  #array of possible orientations
        self.oricorrect = 0  #correct orientation
        
        #Color Training?
        if "color" in training:
            self.colormatters = True #color training on
        else:
            self.colormatters = False
        self.colorrandom = True #randomize color ##TODO: support for arrayed color sequence
        self.colorcorrect = self.black #correct color (default)
        
        #Orientation Training?
        if "orientation" in training:
            self.orientationmatters = True
        else:
            self.orientationmatters = False
        
        #Misc properties
        self.correctfreq = 0.5 #freq of correct stimuli
        self.selectiontime = 30 #how long (in frames) correct stimuli needs to be held in place
                              ##TODO: convert to seconds based on vsync
        self.windowwidth = 200 #width of correct window (pixels)
        self.lapdistance = 1920 #distance between stimuli in pixels (should be higher than screen size /2)
        self.speedgain = 1 #gain of encoder degrees to pixels
        self.objectwidthDeg = 20 #width of stimulus object
        
        self.iscorrect = False #state variable for whether or not current stimulus is correct
        
    def __repr__(self):
        return "Terrain(" + str(self.training) + ')'
        
    def new(self):
        """Gets new terrain settings"""
        if random.random() < self.correctfreq:
            self.correct()
        else:
            self.incorrect()

    def correct(self):
        """Sets the terrain to correct"""
        if self.orientationmatters:
            self.orientation = self.oricorrect
        if self.colormatters:
            self.color = self.colorcorrect
        self.iscorrect = True
        
    def incorrect(self):
        """Sets the terrain to incorrect"""
        #random orientation
        self.orientation = self.getRandomOrientation()
        #random color
        if self.colorrandom:
            self.color = self.getRandomColor()
        self.iscorrect = False
        self.check()

    def getRandomColor(self):
        '''Gets a random color from the palatte '''
        if random.random() < 0.5:
            return self.white
        else:
            return self.black
            
    def getRandomOrientation(self):
        '''Gets a random orientation from the orientation array '''
        r = random.randint(0,len(self.oriarray)-1)
        return self.oriarray[r]
    
    def check(self):
        '''Checks to ensure that we didn't get the correct stimulus somehow for our random incorrect '''
        '''HACK! fix later when N-Dimensional input is completed''' 
        if self.orientationmatters and self.colormatters:
            if self.orientation == self.oricorrect and self.color == self.colorcorrect:
                self.incorrect() #get a new stimulus
        elif self.orientationmatters and not self.colormatters:
            if self.orientation == self.oricorrect:
                self.incorrect() #get a new stimulus
        elif not self.orientationmatters and self.colormatters:
            if self.color == self.colorcorrect:
                self.incorrect() #get a new stimulus
        else:
            pass
            
            
