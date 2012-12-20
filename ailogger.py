# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 14:07:05 2012

@author: derricw
"""

import numpy as np
from numpy import *
import os
import datetime

class ailogger(object):
    """ Creates a logger that writes objects and their values to a file. """
    def __init__(self,path, timestamp = True):
        self.dir = os.path.dirname(path)
        self.filename = os.path.basename(path)
        if timestamp: self.filename = datetime.datetime.now().strftime('%y%m%d%H%M%S') + self.filename
        self.path = os.path.join(self.dir,self.filename)
        if not os.path.exists(self.dir): os.makedirs(self.dir)
        self.f = open(self.path,'w+')
        self.objnames = []
        
    def add(self,*args, **kwargs):
        """ Adds the object to the file. """
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
        """ Adds a comment to the file."""
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
        """ Adds custom string to the file. """
        self.f.write(string)

    def close(self):
        """ Closes the logger. """
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
    log.add('test adding a string arg')
    log.close()

    f = open(path)
    l = f.read()
    f.close()
    print l
    exec(l)
    print t
