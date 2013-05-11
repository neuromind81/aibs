# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 16:19:34 2013

@author: derricw
"""

import scipy.io as sio
from numpy import *
from psychopy import monitors,misc

class StimulusMatFile(object):
    
    def __init__(self, path = None):
        """Creates a mat file object for outputing various values for
            data analysis.
            after loading a .mat file, self.data contains a dictionary of all values.
            
            SOME METHODS ARE FINISHED AND SOME ARE NOT.
            """
        if path is not None: self.loadMat(path)
        
    def loadMat(self,path):
        """ Loads a .mat file """
        self.data = sio.loadmat(path)
        for k,v in self.data.iteritems():
            setattr(self,k,v)
        
    def getOffScreenFrames(self):
        """ Returns a list of frames when the foreground stimulus is offscreen 
            UNFINISHED"""
        objectwidthDeg = int(self.terrain['objectwidthDeg'])
        mon = monitors.Monitors('testMonitor')
        objectwidthPix = misc.deg2pix(objectwidthDeg,mon)
        posx = array(self.posx)

    def getDistanceTraveled(self):
        """ Gets distance traveled by mouse in meters
            Assumes 6" diameter wheel and mouse fixed at 2" radius
        """
        return sum(self.dx)/360*(2*pi*0.051)

    def getRewardsPerMinute(self):
        """ Gets average rewards per minute for whole session."""
        totalminutes = (self.stoptime - self.starttime)/60
        return len(self.rewards)/totalminutes

    def getCorrectPercent(self):
        """ Gets percent of rewards received out of possible.
            Does not discriminate between manually dispensed rewards, but
            will not count more than one reward per lap (so the max is 100%)
        """
        correctlaps = self.getRewardLaps()
        rewardframes = self.rewards[:,1]
        received = 0
        missed = 0
        found = True
        #print self.laps[correctlaps]
        for lap in correctlaps:
            found = False
            for rf in rewardframes:
                if self.laps[lap,1] <= rf < self.laps[min(lap+1,len(self.laps)-1),1]:
                    found = True
            if found: received +=1
            else: missed +=1
        return round(received/float(len(correctlaps))*100.000,3)
        
    def getFalsePositives(self):
        """Gets instances where the mouse tries to choose an incorrect object.
            Output is a vector of frames in which a false positive occurred.
            UNFINISHED
        """
        window = int(self.terrain['windowwidth'])
        selectiontime = int(self.terrain['selectiontime'])
        try: windowx = int(self.terrain['windowx'])
        except: windowx = 0
        posx = self.posx                
        return None

    def getRewardLaps(self):
        """ Gets laps where a reward is possible.  REWRITE FOR TERRAIN THAT USES
                PARAMETERS WITH MULTIPLE CORRECT VALUES!!!
        """
        params = self.terrain['params'][0][0].reshape(-1)
        #correct = list(zip(*[x[0][0]['correct'].reshape(-1).tolist() for x in params])[0]) #WHAT THE FUCK
        correct = array([x[0][0]['correct'].reshape(-1) for x in params]).reshape(-1) #BETTER BUT STILL UGLY
        #print "Correct terrain: ",correct #debugging
        tlog = self.terrainlog[1:]
        correctlaps = []
        for l in range(len(tlog)):
            if tlog[l].tolist()==correct.tolist():
                correctlaps.append(l)
        return array(correctlaps)
        
    def getIncorrectLaps(self):
        """Returns laps that featured an incorrect object."""
        rewardlaps = self.getRewardLaps()
        alllaps = array(range(len(self.laps)))
        incorrectlaps = delete(alllaps,rewardlaps)
        return incorrectlaps
        
        
        
        
def main():
    path = r"\\aibsdata\neuralcoding\Neural Coding\Behavior\130509121003-CA203.mat"
    mat = StimulusMatFile(path)
    fp = mat.getFalsePositives()
    print len(fp)
    return mat
          
if __name__ == "__main__":
    mat = main()
