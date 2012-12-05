'''
Created on Nov 9, 2012

@author: derricw

Reward.py

Simple reward class.  Uses NIDAQ digital IO to trigger a reward (can be anything, we are currently
    using this to flip a relay controlling a valve).
    
TODO: Support for types of rewards other than those controlled by Digital Output
#------------------------------------------------------------------------------ 

#Example use:

see main() below.
    
#------------------------------------------------------------------------------ 
'''
from DigitalIODAQ import DigitalOutput as do
import numpy as np
from threading import Timer
import time

class Reward(object):
    '''
    Reward object.  
    '''

    def __init__(self, device = 1, port = 1, deviceLines = 8, rewardline = 0):
        '''Construct reward '''
        self.dout = do(device,port,deviceLines)
        self.on = np.ones(deviceLines,dtype = np.uint8)
        self.on[rewardline] = 0
        self.off = np.ones(deviceLines,dtype = np.uint8)
        self.rewardtime = 1
        self.rewardcount = 0
        
    def start(self):
        '''Starts IO task '''
        self.dout.StartTask()
        
    def stop(self):
        '''Stops IO task '''
        self.dout.Write(self.off)
        self.dout.StopTask()
        
    def clear(self):
        '''Clears IO task '''
        self.dout.ClearTask()

    def reward(self):
        '''Dispenses reward and starts timer'''
        self.dout.Write(self.on)
        t = Timer(self.rewardtime,self.endreward)
        self.rewardcount += 1
        t.start()
        
    def endreward(self):
        '''Ends the reward after timer ticks '''
        self.dout.Write(self.off)
        
def main():
    reward = Reward(1,1,4,0)  #create a reward object
    reward.start()            #start NIDAQ
    reward.reward()           #trigger reward
    time.sleep(5)             #sleep for 5 seconds
    reward.stop()             #turn on NIDAQ (can be restarted)
    reward.clear()            #clear NIDAQ task (cannot be restarted)
        
        
if __name__ == "__main__":
    main()