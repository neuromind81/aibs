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
        if v is dict:
            listdict[k] = npdict2listdict(v)
        elif v is list or tuple:
            listdict[k] = removenparrays(v)
        else:
            try:
                listdict[k] = v.tolist()
            except:
                try:
                    listdict[k] = list(v)
                except Exception, e:
                    print e
                    listdict[k] = v
    return listdict
    
def removenparrays(listortuple):
    ''' Numpy arrays don't write well as strings.  We convert them to lists '''
    output = []
    try:
        for x in listortuple:
            if x is list or tuple:
                x = removenparrays(x)
            else:
                try:
                    x = x.tolist()
                except:
                    pass
            output.append(x)
    except:
        output = listortuple
    return output


def removeNone(dic, replaceWith = []):
    """  Matlab hates the type "None" Removes the "None" type from a dictionary and all of its elements recursively.  Replaces with [] by default """
    for k,v in dic.iteritems():
        if type(v) is list:
            for x in range(len(v)):
                if v[x] is None: dic[k][x] = replaceWith
        elif type(v) is dict:
            dic[k] = removeNone(v)
        elif v is None:
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
        filename,_ = os.path.splitext(self.fullPath) #remove file ext
        self.matfilepath = filename + ".mat"        
        
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
        if self.genmatfile:
            self.generateMatFile()
        if self.backupFileDir is not None: self.backup()

    def backup(self):
        """ Saves a copy of the file to another directory. """
        if not "test" in self.filename.lower():
            try:
                directory = self.backupFileDir
                if not os.path.exists(directory): os.makedirs(directory)
                fullbackuppath = os.path.join(directory,self.filename)
                shutil.copy(self.fullPath, fullbackuppath)
                if self.genmatfile:
                    filename,_ = os.path.splitext(fullbackuppath)
                    shutil.copy(self.matfilepath,filename+".mat")
                print "Backup to",self.backupFileDir,"performed successfully!"
            except Exception, e:
                print "BACKUP COULD NOT BE PERFORMED!  Ensure that the directory is accessible!",e
        else:
            print "No backup log was generated..."

    def generateMatFile(self):
        """ Saves a copy of the data as a .mat file. """
        data = {}
        for rl in open(self.fullPath).readlines():
            try:
                kvpair = rl.split(" = ",1)
                data[kvpair[0]] = eval(kvpair[1]) #create dictionary
                if data[kvpair[0]] == {}: data[kvpair[0]] = [] #matlab hates empty dictionaries
            except Exception,e:
               print "Could not parse: ", rl, "It will not be included in .mat file.", e
        data = removeNone(data)
        try:
            sio.savemat(self.matfilepath, data) #save .mat file
            print ".mat file generated successfully."
        except Exception, e:
            print "Could not save .mat file.  Check input format.", e
        
    def __repr__(self):
        """ Returns string representation of object """
        return "ailogger(path = " + repr(self.path) + ", " + "timestamp = " + repr(self.timestamp) + ", genmatfile = " + repr(self.genmatfile) + ")"
        
if __name__ == "__main__":
    dic = {}
    dic['a'] = [1, 2, 3]
    dic['b'] = None
    dic['c'] = {'a': 1, 'b': [1,2], 'c': None, 'd': {'a': [1,2]}}
    path = "C:\\Herp\\Derp\\"
    log = ailogger(path)
    log.backupFileDir = "C:\\herp\\derp\\BACKUP\\"
    log.add(dic)
    log.close()