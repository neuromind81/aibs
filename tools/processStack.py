# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 12:41:54 2013

@author: derricw
"""
import os
from fijitools import runScript
from wavefromtif import processSequence

#LOCATION OF FIJI EXECUTABLE
path = r"C:\fiji-win64\Fiji.app\ImageJ-win64.exe"
#LOCATION OF FIJI stacklist2images.py SCRIPT
script = r"C:\Users\derricw\Desktop\WinPython-64bit-2.7.3.3\python-2.7.3.amd64\Lib\site-packages\aibs\tools\stacklist2imagesheadless.py"

#LOCATION OF STACK
stack = r"C:\Users\derricw\Documents\data130307\images\CA170_130205_a\ch3"

print "Unpacking image sequence at:",stack
runScript(path,script,stack)
sequence = os.path.join(stack,"sequence\\")

#PATH FOR OUTPUT
output = r"C:\Users\derricw\Documents\data130307\seqoutput.mat"

#GO!!!
processSequence(sequence,output)