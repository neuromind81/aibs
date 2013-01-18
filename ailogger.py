# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 14:07:05 2012

@author: derricw

Logs objects and their python code representation to a file.

##TODO: Matlab output mode.

Example useage:

see main() for an example.


"""

import numpy as np
from numpy import *
import os
import datetime
import shutil
import stat

def npdict2listdict(npdict):
    """ Converts a dictionary with numpy arrays to a dictionary with lists """
    listdict = {}
    for k,v in npdict.iteritems():
        try:
            listdict[k] = v.tolist()
        except:
            listdict[k] = v
    return listdict

class ailogger(object):
    """ Creates a logger that writes objects and their values to a file. """
    def __init__(self,path, timestamp = True):
        self.path = path
        self.dir = os.path.dirname(path)
        self.filename = os.path.basename(path)
        self.timestamp = timestamp
        if self.timestamp: self.filename = datetime.datetime.now().strftime('%y%m%d%H%M%S') + '-' + self.filename
        self.fullPath = os.path.join(self.dir,self.filename)
        if not os.path.exists(self.dir): os.makedirs(self.dir)
        self.f = open(self.fullPath,'w+')
        self.objnames = []

        self.backupFileDir = None
        self.readOnly = True
        
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
        """ Closes the logger. [Sets read only status. Backs up the file.] """
        self.f.close()
        if self.readOnly: os.chmod(self.fullPath,stat.S_IREAD)
        if self.backupFilePath is not None: self.backup()

    def backup(self):
        """ Saves a copy of the file to another directory. """
        try:
            directory = os.path.dirname(self.backupFilePath)
            if not os.path.exists(directory): os.makedirs(directory)
            shutil.copy(self.fullPath, directory)
        except:
            print "BACKUP COULD NOT BE PERFORMED!  Ensure that the directory is accessible!"
        
    def __repr__(self):
        """ Returns string representation of object """
        return "ailogger(path = " + repr(self.path) + ", " + "timestamp = " + repr(self.timestamp) + ")"
        
if __name__ == "__main__":
    path = 'C:\\ExperimentData\\test3\\'
    log = ailogger(path)
    log.backupFilePath = 'C:\\Herp\\Backup\\'
    testlist = range(1000)
    test = np.array(testlist)
    testdict = {'test':test}
    log.add(t = npdict2listdict(testdict))
    log.add(1)
    log.comment("this is a comment that i haven't added a # to")
    log.add(balls = [456.7])
    log.comment("#this is a comment that I added a # to")
    log.add('test adding a string arg')
    dic = {'a':5, 'b':[1,2,3]}
    log.add(dic = dic)
    log.close()

