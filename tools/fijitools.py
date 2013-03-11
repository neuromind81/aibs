# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 10:42:32 2013

@author: derricw
"""

import subprocess

def runScript(path, script = None, arg = None):
    string = path
    if script is not None:
        string += " " + script
    if arg is not None:
        string += " " + arg
    print "Calling",string
    subprocess.call(string)

if __name__ == "__main__":
    path = r"C:\fiji-win64\Fiji.app\ImageJ-win64.exe"
    script = r"C:\Users\derricw\Desktop\WinPython-64bit-2.7.3.3\python-2.7.3.amd64\Lib\site-packages\aibs\tools\stacklist2imagesheadless.py"
    arg = r"C:\Users\derricw\Documents\data130307\images\CA170_130205_a\ch3"
    runScript(path,script,arg)