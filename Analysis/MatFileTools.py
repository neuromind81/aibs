# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 16:19:34 2013

@author: derricw
"""

import scipy.io as sio
from pylab import *
import numpy as np
from psychopy import monitors,misc
import os
from aibs.Analysis.Core import smooth

class MatFile(object):
    """ Base Class for MatFile object

        Arguments:
        "path": full path of the mat file.

    """

    def __init__(self, path, *args, **kwargs):

        for k,v in kwargs.iteritems():
            setattr(self,k,v)

        if path is not None: self.loadMat(path)

    def loadMat(self,path):
        """ Loads a .mat file """
        self.path = path
        self.filename = os.path.basename(path)
        self.data = sio.loadmat(self.path)
        for k,v in self.data.iteritems():
            setattr(self,k,v)


class StimulusMatFile(MatFile):
    """Class for a generic stimulus mat file."""
    def __init__(self, *args, **kwargs):
        super(StimulusMatFile, self).__init__(*args,**kwargs)
        

class BehaviorMatFile(StimulusMatFile):
    """Class for a generic behavior mat file."""
    def __init__(self, *args,**kwargs):
        super(BehaviorMatFile, self).__init__(*args,**kwargs)

    def getTotalSeconds(self):
        """Returns length of experiment in seconds."""
        return float(self.stoptime-self.starttime)

    def getTotalMinutes(self):
        """Returns length of experiment in minutes."""
        return self.getTotalSeconds()/60


class ForagingMatFile(BehaviorMatFile):
    
    def __init__(self, *args, **kwargs):
        """Creates a mat file object for outputing various values for
            data analysis.
            after loading a .mat file, self.data contains a dictionary of all values.
            
            SOME METHODS ARE FINISHED AND SOME ARE NOT.
            """
        super(ForagingMatFile, self).__init__(*args,**kwargs)
        
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
        totalminutes = getTotalMinutes()
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
        
    def plotVelocity(self,showPlot=True,ax=None):
        """Plots wheel velocity vs time."""
        traw = arange(len(self.dx))/60.00
        vraw = self.dx.reshape(-1)*60
        vsmooth = smooth(vraw,window_len=60)
        tsmooth = arange(len(vsmooth))/60.00
        if ax is None:
            plot(traw,vraw)
            plot(tsmooth,vsmooth,linewidth=2.0)
            title('Velocity vs Time')
            xlabel('Elapsed Time (sec)')
            ylabel('Velocity (deg/sec)')
            legend(['Raw Data','Smoothed'])
        else:
            ax.plot(traw,vraw)
            ax.plot(tsmooth,vsmooth,linewidth=2.0)
            ax.set_title('Velocity vs Time')
            ax.set_xlabel('Elapsed Time (sec)')
            ax.set_ylabel('Velocity (deg/sec)')
            ax.legend(['Raw Data','Smoothed'])
        if showPlot:
            show(True)

    def plotJourney(self,showPlot=True,ax=None):
        """Plots cumulative distance traveled vs time."""
        t = arange(len(self.dx))/60.00
        cumdist = cumsum(self.dx)/360*2*pi*.051 #assuming 6" wheel and mouse at 2" radius
        if ax is None:
            plot(t,cumdist)
            title('Mouse Journey')
            xlabel('Time elapsed (s)')
            ylabel('Distance traveled (m)')
            legend(['Cumulative Distance'])
        else:
            ax.plot(t,cumdist)
            ax.set_title('Mouse Journey')
            ax.set_xlabel('Time elapsed (s)')
            ax.set_ylabel('Distance traveled (m)')
            ax.legend(['Cumulative Distance'])
        if showPlot:
            show(True)

    def plotStops(self,showPlot=True,ax=None):
        """Plots mouse stopage for correct and incorrect windows.
            UNFINISHED
        """
        posx=self.posx
        
        
    def plotAll(self,output=None):
        """Plots all relevant plots in a single figure.
           Can output to pdf or png.
           OUTPUT IS NOT FINISHED"""
        f0,axs = subplots(1,2)
        self.plotJourney(False,axs[0])
        self.plotVelocity(False,axs[1])
        tight_layout()
        show()
        if output == "pdf":
            pass
        elif output == 'png':
            pass

def main():
    path = r"\\aibsdata\neuralcoding\Neural Coding\Behavior\130514111245-CA244_S5T1.mat"
    mat = ForagingMatFile(path = path)
    mat.plotAll()

          
if __name__ == "__main__":
    mat = main()
