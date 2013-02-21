# -*- coding: utf-8 -*-
"""
Created on Wed Feb 20 21:10:51 2013

@author: derricw
"""

from psychopy import visual

def replay(logstringarray, saveframes = False):
    
    log = {}
    #get log info
    for rl in logstringarray:
        line = rl.split(' = ',1)
        try:
            log[line[0]] = eval(line[1])
        except Exception, e:
            pass
        
    #get script text
    scripttext = log['scripttext']
    minusrun = scripttext.replace('.run()','.getFrame()') 
    
    if saveframes:
        exec(minusrun)
        g.saveframes = True
        g.run()
    #rerun experiment
    exec(scripttext)
        
        
    
def getFrameInfo(logstringarray):
    log = {}
    #get log info
    for rl in logstringarray:
        line = rl.split(' = ',1)
        try:
            log[line[0]] = eval(line[1])
        except Exception, e:
            pass
        
    #get script text
    scripttext = log['scripttext']
    minusrun = scripttext.replace('.run()','.getFrame()') 
    
    #load experiment
    exec(minusrun)
    #get vsync numbers
    
    preexpframes = int(params['preexpsec']*60)
    postexpframes = int(params['postexpsec']*60)
    sweepframes = int(params['sweeplength']*60)
    postsweepframes = int(params['postsweepsec']*60)
    
    
    
            
    
    

    
    
if __name__=="__main__":
    
    path = r"C:\ExperimentLogs\130220210939-Spock.log"
    f = open(path,'r').readlines()
    frame = replay(f,True)

    