'''
Created on Nov 1, 2012

@author: derricw
#------------------------------------------------------------------------------ 
Encoder.py
#------------------------------------------------------------------------------ 

Supports magnetic rotary encoders like this one:
http://www.usdigital.com/assets/datasheets/MA3_datasheet.pdf?k=634873722481273530

Dependencies:
Python2X
PyDAQmx  (http://pypi.python.org/pypi/PyDAQmx)
AnalogIODAQ (Derric's wrapper for PyDAQmx Analog Input, get it from him)
numpy (http://www.scipy.org/Download)

Example usage:
#------------------------------------------------------------------------------ 
    e = Encoder.Encoder('Dev1',0,1,'analog',500)
    e.start()
    e.accumulateData()
    time.sleep(1) #collect some data
    
    print e.getDegrees()
    print e.getVin()
    print e.getVsig()
    
    e.stopAccumulatingData()
    data = e.getAllData()
    deg = e.getDegrees(2, data)

    e.clear()
    
    print deg
    print len(deg)
#------------------------------------------------------------------------------ 
    
'''
#----------------------------------------------------------------------- Imports
from AnalogIODAQ import AnalogInput as ait

#--------------------------------------------------------------------- Functions
#Gets degrees from supply voltage and signal voltage
def Degrees(vin,vsig):
    try:
        angle = vsig/vin*360
    except:
        angle = 0 #avoids divide by zero errors
    return angle #rounds to two decimal points
    
#----------------------------------------------------------------------- Classes
class Encoder():
    '''
    Creates a new rotary encoder object.
    
    Inputs
    device (which NI device)
    vin (which channel has supply voltage)
    vsig (which channel has signal voltage)
    type (what type of encoder)
    buffer (the size of data buffer you'd like to maintain on the NIDAQ)
    
    All of these values have defaults below.
    Currently no support for PWM encoders, only analog.

    '''
    def __init__(self, device = 'Dev1', vin = 0, vsig = 1, type = 'analog', buffer = 100):
        '''
        Constructor
        '''
        self.device = device
        self.vin = vin
        self.vsig = vsig
        self.type = type
        self.buffer = buffer
        
        self.noEObject = 'No valid encoder object has been created.'
        
        if type == 'analog':
            self.AISignal = ait(device,[vsig,vin],buffer) #Device 1, Channels 2 and 1
        else:
            print 'No support for ' + type + 'encoders.'
            self.AISignal = None
            
    def __repr__(self):
        return "Encoder('" + self.device + "'," + str(self.vin) + ',' + str(self.vsig) + ",'" + self.type + "'," + str(self.buffer) + ')'
    
     
    def start(self):
        '''Starts the NIDAQ Task'''
        if self.AISignal is not None:
            self.AISignal.StartTask()
        else:
            print self.noEObject
            

    def stop(self):
        '''Stops the NIDAQ Task'''
        if self.AISignal is not None:
            self.AISignal.StopTask()
        else:
            print self.noEObject
            

    def clear(self):
        '''Clears the NIDAQ Task'''
        if self.AISignal is not None:
            self.AISignal.StopTask()
            self.AISignal.ClearTask()
        else:
            print self.noEObject
            
     
    def getVin(self):
        '''Gets most current Vin'''
        if self.AISignal is not None: 
            vin = self.AISignal.data[self.buffer-1][1]
        else:
            vin = 0
        return vin
    

    def getVsig(self):
        '''Gets most current Vsig'''
        if self.AISignal is not None: 
            vsig = self.AISignal.data[self.buffer-1][0]
        else:
            vsig = 0
        return vsig
    

    def getDegrees(self, data = []):
        '''Gets most current degrees
            Can also be used to convert an array of data to an array of degrees'''
        vsig = self.getVsig()
        vin = self.getVin()
        if data == []:
            return Degrees(vin,vsig)
        else:
            try:
                degArray = []
                for d in data:
                    degArray.append(Degrees(d[1],d[0]))
                return degArray
            except:
                print 'Data incorrectly formatted.'
                return []
        

    def accumulateData(self):
        '''Starts data accumulation.  Data is retrieved after accumulation using getAllData()'''
        if self.AISignal is not None:
            self.AISignal.accumulate = True
    

    def stopAccumulatingData(self):
        '''Stops data accumulation'''
        if self.AISignal is not None:
            self.AISignal.accumulate = False
    
      
    def getAllData(self):
        '''Gets all accumulated data'''
        data = []
        if self.AISignal is not None:
            data = self.AISignal.dataArray
        return data    
    
        
            
        