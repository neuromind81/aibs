'''
Created on Oct 26, 2012

@author: derricw
#------------------------------------------------------------------------------ 
DigitalIODAQ.py
#------------------------------------------------------------------------------ 

Derric's wrapper for Digital IO from an NIDAQ board using the PyDAQmx library.

List of features to add in the future:
1) Buffered reading and writing with clock timing
2) TDMS data logging
3) ???


Dependencies:
Python27
PyDAQmx (http://pypi.python.org/pypi/PyDAQmx)
numpy (http://www.scipy.org/Download)

NIDAQmc C++ Reference:  #PyDAQmx maps one-to-one to the C++ library
http://zone.ni.com/reference/en-XX/help/370471W-01/

Examples usage:
#------------------------------------------------------------------------------ 
    
    # Get device info example    
    dev = GetDevices() #get all devices
    for d in dev:
        print d
        print GetDILines(d) #get all DI lines
        print GetDOLines(d) #get all DO lines    
    
    # Digital outout example
    task = DigitalOutput('Dev1',1) #device 1, port 1
    task.StartTask()
    
    data = np.array([1,0,1,0],dtype = np.uint8)
    
    task.Write(data)
    
    task.StopTask()
    task.ClearTask()
    
    
    # Digital Input Example
    task = DigitalInput('Dev1',0) #device 1, port 0
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
    
def GetDOPorts(device):
    """Returns the names of all Digital Output ports on the specified device"""
    buffersize = 1024
    ports = " "*buffersize
    DAQmxGetDevDOPorts(device, ports, buffersize)
    return ports.strip().strip('\x00').split(', ')

def GetDIPorts(device):
    """Returns the names of all Digital Input ports on the specified device"""
    buffersize = 1024
    ports = " "*buffersize
    DAQmxGetDevDIPorts(device, ports, buffersize)
    return ports.strip().strip('\x00').split(', ')

def GetDOLines(device):
    """Returns the names of all Digital Output lines on the specified device"""
    buffersize = 1024
    lines = " "*buffersize
    DAQmxGetDevDOLines(device, lines, buffersize)
    return lines.strip().strip('\x00').split(', ')
    
def GetDILines(device):
    """Returns the names of all Digital Input lines on the specified device"""
    buffersize = 1024
    lines = " "*buffersize
    DAQmxGetDevDILines(device, lines, buffersize)
    return lines.strip().strip('\x00').split(', ')

#-------------------------------------------------------------------- Input Task
class DigitalInput(Task):
    '''
    Gets the state of the inputs from the NIDAQ Device/port specified. 
        Different devices have different number of lines.  Tested on a
        device with 4 input lines
    '''
    def __init__(self, device = GetDevices()[0] ,port = GetDIPorts(GetDevices()[0])[0][-1]):
        
        """
        Constructor for DI Object
            Will get default device and port if none are specified.
        """

        Task.__init__(self)
        
        lines = GetDILines(device)
        lines = [l for l in lines if 'port' + str(port) in l]
        self.deviceLines = len(lines)
        
        #set up task properties
        devStr = str(device) + "/port" + str(port) + "/line0:" + str(self.deviceLines-1)
            
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
    Sets the current output state of all digital lines.  Input is device name, output port #.
        Tested on a device with 4 output lines.
    '''
    def __init__(self, device = GetDevices()[0], port = GetDOPorts(GetDevices()[0])[0][-1]):
        """
        Constructor for DO object
            If no port is specified, gets default port from default device.
        """
        
        Task.__init__(self)
        
        lines = GetDOLines(device)
        lines = [l for l in lines if 'port' + str(port) in l]
        self.deviceLines = len(lines)  
        
        #create dev str for various lines
        devStr = str(device) + "/port" + str(port) + "/line0:" + str(self.deviceLines-1)

        self.lastOut = np.zeros(self.deviceLines, dtype = np.uint8) #keep track of last output #should be gotten from initial state instead

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
    
    dev = GetDevices() #get all devices
    for d in dev:
        print d
        print GetDILines(d) #get all DI lines
        print GetDOLines(d) #get all DO lines
        
        print GetDOPorts(d)
    
    #Digital Input Example
    task = DigitalOutput() #device 1, port 0
    task.StartTask()

    task.StopTask()
    task.ClearTask()
    
    
#----------------------------------------------------------------------- IF MAIN
if __name__ == "__main__":
    main()
