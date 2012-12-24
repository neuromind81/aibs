'''
Created on Oct 26, 2012

@author: derricw
#------------------------------------------------------------------------------ 
DigitalIODAQ.py
#------------------------------------------------------------------------------ 

Derric's wrapper for Digital IO from an NIDAQ board using the PyDAQmx library.

List of features to add in the future:
1) Buffered reading and writing with clock timing
2) Task should automatically get port/line numbers (if possible via NI api)
3) TDMS data logging
4) ???


Dependencies:
Python27
PyDAQmx (http://pypi.python.org/pypi/PyDAQmx)
numpy (http://www.scipy.org/Download)

NIDAQmc C++ Reference:  #PyDAQmx maps one-to-one to the C++ library
http://zone.ni.com/reference/en-XX/help/370471W-01/

Examples usage:
#------------------------------------------------------------------------------ 
    
    #Digital outout example
    task = DigitalOutput(1,1,4) #device 1, port 1, 4 lines
    task.StartTask()
    
    data = np.array([1,0,1,0],dtype = np.uint8)
    
    task.Write(data)
    
    task.StopTask()
    task.ClearTask()
    
    
    #Digital Input Example
    task = DigitalInput(1,0,4) #device 1, port 0, 4 lines
    task.StartTask()
    
    data = task.Read()
    
    print data
    
    task.StopTask()
    task.ClearTask()
    
#------------------------------------------------------------------------------ 


'''
#----------------------------------------------------------------------- Imports
from PyDAQmx import Task
from PyDAQmx.DAQmxConstants import *
from PyDAQmx.DAQmxFunctions import *
import numpy as np
from ctypes import c_long, c_ulong


#-------------------------------------------------------------- Config Functions
def GetDevices():
    """Gets all NIDAQ devices and returns a list of their names"""
    buffersize = 1024 #set max buffer size
    devicenames = " "*buffersize #build device string
    DAQmxGetSysDevNames(devicenames, buffersize) #fill string with names
    return devicenames.strip().strip('\x00').split(', ')  #strip off null char for each

#-------------------------------------------------------------------- Input Task
class DigitalInput(Task):
    '''
    Gets the state of the inputs from the NIDAQ Device/port specified.  Lines is number of IO
        lines on the port.  Different devices have different number of lines.  Tested on a
        device with 4 input lines
    '''
    def __init__(self,device = 1,port = 0,lines = 8):
        #construct task
        Task.__init__(self)
        
        #set up task properties
        devStr = "Dev" + str(device) + "/port" + str(port) + "/line0:" + str(lines-1)
        self.deviceLines = lines
            
        #create channel
        self.CreateDIChan(devStr,"",DAQmx_Val_ChanForAllLines)
        '''
        http://zone.ni.com/reference/en-XX/help/370471W-01/daqmxcfunc/daqmxcreatedichan/
        '''
        
    def Read(self):
        #reads the current setting of all inputs
        data = np.zeros(self.deviceLines, dtype = np.uint8)
        bytesPerSample = c_long()
        samplesPerChannel = c_long()
        self.ReadDigitalLines(1,10.0,DAQmx_Val_GroupByChannel,data,self.deviceLines,
                              samplesPerChannel,bytesPerSample,None)
        '''
        http://zone.ni.com/reference/en-XX/help/370471W-01/daqmxcfunc/daqmxreaddigitallines/
        '''
        return data
        
    def DoneCallback(self, status):
        print "Status",status.value
        return 0 # The function should return an integer

#------------------------------------------------------------------- Output Task
class DigitalOutput(Task):
    '''
    Sets the current output state of all digital lines.  Input is device #, output port #,
        and number of output lines on device.  Tested on a device with 4 output lines.
    '''
    def __init__(self, device = 1, port = 0, deviceLines = 8):
        Task.__init__(self)
        #create dev str for various lines
        ##TODO: Get these values from the device instad, as well as current line states
        devStr = "Dev" + str(device) + "/port" + str(port) + "/line0:" + str(deviceLines-1)

        self.lastOut = np.zeros(deviceLines, dtype = np.uint8) #keep track of last output

        #create IO channel
        self.CreateDOChan(devStr,"",DAQmx_Val_ChanForAllLines)
        '''
        http://zone.ni.com/reference/en-XX/help/370471W-01/daqmxcfunc/daqmxcreatedochan/
        '''
        self.AutoRegisterDoneEvent(0)
        
    def DoneCallback(self,status):
        print "Status", status.value
        return 0
    
    def Write(self,data):
        '''Writes a numpy array of data to set the current output state'''
        self.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,data,None,None)
        self.lastOut = data
        '''
        http://zone.ni.com/reference/en-XX/help/370471W-01/daqmxcfunc/daqmxwritedigitallines/
        '''

    def WriteBit(self, index, value):
        '''Writes a single bit to the given line index NOT TESTED '''
        self.lastOut[index] = value
        self.WriteDigitalLines(1,1,10.0,DAQmx_Val_GroupByChannel,self.lastOut,None,None)
        
#-------------------------------------------------------------------------- Main
def main():
    
    '''
    task = DigitalOutput(1,1,4) #device 1, port 1, 4 lines
    task.StartTask()
    
    data = np.array([1,1,1,1],dtype = np.uint8)
    
    task.Write(data)
    
    task.StopTask()
    task.ClearTask()
    '''
    dev = GetDevices()
    print dev
    print len(dev)
    
    
#----------------------------------------------------------------------- IF MAIN
if __name__ == "__main__":
    main()
