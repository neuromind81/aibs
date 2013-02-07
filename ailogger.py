# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 14:07:05 2012

@author: derricw

Logs objects and their python code representation to a file.  Also generates .mat files unless
    explicitly told not to.

Example useage:

see main() for an example.


"""

import numpy as np
from numpy import *
import os
import datetime
import shutil
import stat
import scipy.io as sio

def npdict2listdict(npdict):
    """ Converts a dictionary with numpy arrays to a dictionary with lists """
    listdict = {}
    for k,v in npdict.iteritems():
        try:
            listdict[k] = v.tolist()
        except:
            listdict[k] = v
    return listdict

def removeNone(dic, replaceWith = []):
    """ Removes the "None" type from a dictionary and all of its elements recursively.  Replaces with [] by default """
    for k,v in dic.iteritems():
        if type(v) is list:
            for x in range(len(v)):
                if v[x] is None: dic[k][x] = replaceWith
        if type(v) is dict:
            dic[k] = removeNone(v)
        if v is None:
            dic[k] = replaceWith
    return dic

class ailogger(object):
    """ Creates a logger that writes objects and their values to a file. """
    def __init__(self,path, timestamp = True, genmatfile = True):
        self.path = path
        self.dir = os.path.dirname(path)
        self.filename = os.path.basename(path)
        self.timestamp = timestamp
        self.genmatfile = genmatfile
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
        if self.backupFileDir is not None: self.backup()
        if self.genmatfile:
            self.generateMatFile()
            print "Mat file generated successfully."

    def backup(self):
        """ Saves a copy of the file to another directory. """
        try:
            directory = os.path.dirname(self.backupFileDir)
            if not os.path.exists(directory): os.makedirs(directory)
            shutil.copy(self.fullPath, directory)
        except:
            print "BACKUP COULD NOT BE PERFORMED!  Ensure that the directory is accessible!"

    def generateMatFile(self):
        """ Saves a copy of the file as a .mat file. """
        data = {}
        for rl in open(self.fullPath).readlines():
            try:
                kvpair = rl.split(" = ",1)
                data[kvpair[0]] = eval(kvpair[1]) #create dictionary
            except Exception,e:
                print "Could not parse: ", rl, "It will not be included in .mat file.", e
        data = removeNone(data)
        filename, fileext = os.path.splitext(self.fullPath) #remove file ext
        try:
            sio.savemat(filename + ".mat", data) #save .mat file
        except:
            print "Could not save .mat file.  Check input format."
        
    def __repr__(self):
        """ Returns string representation of object """
        return "ailogger(path = " + repr(self.path) + ", " + "timestamp = " + repr(self.timestamp) + ")"
        
if __name__ == "__main__":
    dic = {}
    dic['a'] = [1, 2, 3]
    dic['b'] = None
    dic['c'] = {'a': 1, 'b': [1,2,3], 'c': None, 'd': {'a': [1,2]}}
    path = r"C:\Herp\Derp.log"
    log = ailogger(path)
    log.add(dic)
    log.close()