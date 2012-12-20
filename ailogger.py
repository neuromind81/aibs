# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 14:07:05 2012

@author: derricw
"""

import numpy as np
from numpy import *
import os

class ailogger(object):
    def __init__(self,path):
        self.dir = os.path.dirname(path)
        self.filename = os.path.basename(path)
        if not os.path.exists(self.dir): os.makedirs(self.dir)
        self.f = open(path,'w+')
        self.objnames = []
        
    def add(self,*args, **kwargs):
        for a in args:
            t = type(a).__name__
            i = 0
            name = t + str(i)
            while t in self.objnames:
                i += 1
                name = "%s%i" % (t,i)
            self.objnames.append(name)
            string = "%s = %s\n" % (name,repr(a))
            self.f.write(string)
                
        for k,v in kwargs.iteritems():
            string = "%s = %s\n" % (k, repr(v))
            self.f.write(string)

    def comment(self, comment, multiline = False):
        if not multiline:
            if comment[0] == "#":
                string = comment + '\n'
            else:
                string = "#" + comment + '\n'
            self.f.write(string)
        else:
            if comment[:2] == '"""' or comment[:2] == "'''":
                string = comment + '\n'
            else:
                string = "'''" + comment + "'''\n"
            self.f.write(string)
                
    def addstr(self,string):
        self.f.write(string)

    def close(self):
        self.f.close()
        
        
if __name__ == "__main__":
    path = r'C:\Herp\Derp\log1.dat'
    log = ailogger(path)
    test = np.array(['a','b','c'])
    log.add(t = test)
    log.add(1)
    log.comment("this is a comment that i haven't added a # to")
    log.add(balls = [456.7])
    log.comment("#this is a comment that I added a # to")
    #log.addstr('This is a string that I have added')
    log.add('test adding a string arg')
    log.close()

    f = open(path)
    l = f.read()
    f.close()
    print l
    exec(l)
    print t
