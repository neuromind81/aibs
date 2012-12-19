# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 14:07:05 2012

@author: derricw
"""

import os

class ailogger(object):
    def __init__(self,path):
        self.dir = os.path.dirname(path)
        self.filename = os.path.basename(path)
        if not os.path.exists(self.dir): os.makedirs(self.dir)
        self.f = open(path,'w+')
        
    def add(self,*args, **kwargs):
        for a in args:
            t = type(a)
            print t.__name__
        for k,v in kwargs.iteritems():
            string = "%s = %s\n" % (k, repr(v))
            self.f.write(string)

    def close(self):
        self.f.close()
        
        
if __name__ == "__main__":
    path = r'C:\Herp\Derp\log1.dat'
    log = ailogger(path)
    test = [1,2,3]
    log.add(test, test = test)
    log.close()