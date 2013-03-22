'''
Created on Oct 18, 2012

@author: derricw
'''

import os
import sys
from PyQt4 import QtCore as qt, QtGui
from PyQt4.QtCore import QObject as qo
from ForagingGuiLayout import Ui_MainWindow
from rewarddiaglayout import Ui_Form
from psychopy import visual
from ScriptGenerator import Script
import subprocess
from datetime import datetime
from aibs.Terrain import Terrain
from aibs.Core import *

 
class MyForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        """Constructor for main form."""
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #Set up other forms
        self.rewarddiag = None
        
        # Set up some directories
        self.library = getdirectories()
        self.logDir = os.path.join(self.library,'BehaviorLogs')
        self.experimentslib = os.path.join(self.library,'Experiments')
        self.stimulilib = os.path.join(self.library,'Stimuli')
        self.terrainlib = os.path.join(self.library,'Terrain')
        self.scriptlog = os.path.join(self.library,'ScriptLog')

        ''' Delete if above works on windows
        self.library = "C:\\AibsStim\\"
        self.logDir = "C:\\BehaviorLogs\\"
        self.experiments = "C:\\AibsStim\\Experiments\\"
        self.stimuli = "C:\\AibsStim\\Stimuli\\"
        self.terrain = "C:\\AibsStim\\Terrain\\"
        '''
        
        # Set up some important variables
        self.params = {}
        self.bgSweep = {}
        self.fgSweep = {}
        self.terrainText = None
        self.bgStimText = None
        self.fgStimText = None

        # Set up some defaults (can be overwritten by config file)
        self.nidevice = 'Dev1'
        self.rewardport = '0'
        self.rewardline = '0'
        self.encodervsigchannel = '0'
        self.encodervinchannel = '1'
        self.backupdir = ''
        self.screen = 0
        self.monitor = 'testMonitor'
        self.syncsqr = 'True'
        self.syncsqrloc = (-500,-500)
        
        # Read config file
        try:
            f = open("foraging.cfg")
            for rl in f.readlines():
                line = rl.split("=")
                setattr(self,line[0], line[1])
            f.close()
        except:
            print "Could not read config file.  Using default values."
        
        # Add information to relevant fields
        self.ui.lineEdit_logDir.setText(self.logDir)
        
        # Ensure important directories exist, create them if not.
        checkDirs(self.logDir,self.library,self.stimulilib,self.experimentslib,self.terrainlib,self.scriptlog)
        
        # Connect signals
        qo.connect(self.ui.pushButton_loadExperiment,qt.SIGNAL("clicked()"), self._loadExperiment)
        qo.connect(self.ui.pushButton_loadBGStimulus,qt.SIGNAL("clicked()"), self._loadBG)
        qo.connect(self.ui.pushButton_loadFGStimulus,qt.SIGNAL("clicked()"), self._loadFG)
        qo.connect(self.ui.pushButton_loadTerrain,qt.SIGNAL("clicked()"), self._loadTerrain)
        qo.connect(self.ui.pushButton_run,qt.SIGNAL("clicked()"), self._run)
        qo.connect(self.ui.pushButton_displayTerrain,qt.SIGNAL("clicked()"), self._preview)
        qo.connect(self.ui.pushButton_rewardDiagnostic,qt.SIGNAL("clicked()"),self._rewarddiag)

        ''' Examples of connecting signals (assumes your form has a pushButton, lineEdit, and textEdit)
        #QtCore.QObject.connect(self.ui.pushButton, QtCore.SIGNAL("clicked()"), self.ui.textEdit.clear )
        #QtCore.QObject.connect(self.ui.lineEdit, QtCore.SIGNAL("returnPressed()"), self.add_entry)
        '''
        ''' Example of signal callback (performed when return is pressed on lineEdit, see above)
    def add_entry(self):
        self.ui.lineEdit.selectAll()
        self.ui.lineEdit.cut()
        self.ui.textEdit.append("")
        self.ui.textEdit.paste()
        '''
        
    def _loadExperiment(self):
        """Load an experiment file."""
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.experimentslib)
        try:
            f = open(fname, 'r')
            with f:        
                data = f.read()
                try:
                    exec(data)
                    self.params = params
                    index = 0
                    for k,v in params.iteritems():
                        self.ui.tableWidget_experiment.setItem(index,0,QtGui.QTableWidgetItem(str(k)))
                        self.ui.tableWidget_experiment.setItem(index,1,QtGui.QTableWidgetItem(str(v)))
                        index +=1
                    self.ui.tableWidget_experiment.sortByColumn(0,0)
                    _,tail = os.path.split(str(fname)) #get just the file name
                    self.ui.groupBox_ExperimentParams.setTitle(tail)
                except Exception, e:
                    print "Data is incorrectly formatted.",e
        except Exception, e:
            print "Couldn't open file:",e

    
    def _loadBG(self):
        """Load a stimulus file as the background stimulus."""
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.stimulilib)
        try:
            f = open(fname, 'r')
            with f:        
                data = f.read()
                stim = data.split('PARAMETERS',1) #only care about parameters
                self.bgStimText = stim[0]
                try:
                    exec(stim[1]) #excupt only parameters
                    index = 0
                    for k,v in bgSweep.iteritems():
                        self.ui.tableWidget_bgStimulus.setItem(index,0,QtGui.QTableWidgetItem(str(k)))
                        self.ui.tableWidget_bgStimulus.setItem(index,1,QtGui.QTableWidgetItem(str(v)))
                        index +=1
                    self.ui.tableWidget_experiment.sortByColumn(0,0)
                    _,tail = os.path.split(str(fname)) #get just the file name
                    self.ui.groupBox_BgStimulus.setTitle(tail)
                except Exception, e:
                    print "Data is incorreclty formatted.",e
                    
        except Exception, e:
            print "Couldn't open file:",e
    
    def _loadFG(self):
        """Load a stimulus file as the foreground stimulus."""
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.stimulilib)
        try:
            f = open(fname, 'r')
            with f:        
                data = f.read()
                stim = data.split('PARAMETERS',1) #only care about parameters
                self.fgStimText = stim[0]
                try:
                    exec(stim[1]) #execute only parameters
                    index = 0
                    for k,v in fgSweep.iteritems():
                        self.ui.tableWidget_fgStimulus.setItem(index,0,QtGui.QTableWidgetItem(str(k)))
                        self.ui.tableWidget_fgStimulus.setItem(index,1,QtGui.QTableWidgetItem(str(v)))
                        index +=1
                    self.ui.tableWidget_experiment.sortByColumn(0,0)
                    _,tail = os.path.split(str(fname)) #get just the file name
                    self.ui.groupBox_FgStimulus.setTitle(tail)
                except Exception, e:
                    print "Data is incorreclty formatted.",e
                    
        except Exception, e:
            print "Couldn't open file:",e
        
    def _loadTerrain(self):
        """Load a terrain file as the terrain."""
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.terrainlib)
        try:
            f = open(fname, 'r')
            with f:        
                data = f.read()
                try:
                    exec(data) #execute only parameters
                    index = 0
                    for k,v in terrain.__dict__.iteritems():
                        self.ui.tableWidget_terrainParams.setItem(index,0,QtGui.QTableWidgetItem(str(k)))
                        self.ui.tableWidget_terrainParams.setItem(index,1,QtGui.QTableWidgetItem(str(v)))
                        index +=1
                    self.ui.tableWidget_experiment.sortByColumn(0,0)
                    _,tail = os.path.split(str(fname)) #get just the file name
                    self.ui.groupBox_Terrain.setTitle(tail)
                except Exception, e:
                    print "Data is incorreclty formatted.",e
        except Exception, e:
            print "Couldn't open file:",e
    
    def _run(self):
        """Runs an experiment."""
        print "Generating script..."
        script = self._generateScript()
        print script.script
        print "Checking script..."
        #self._checkScript()
        print "Saving script..."
        dt = datetime.now().strftime('%y%m%d%H%M%S')
        path = os.path.join(self.scriptlog,dt+str(self.ui.lineEdit_mouseid.text())+".py")
        script.save(path)
        print "Script saved at",path
        print "Running experiment..."
        execstring = "python "+path
        sp = subprocess.Popen(execstring.split())
        

        
    def _generateScript(self):
        """"Generates a Foraging script based on GUI input fields."""
        #CREATE SCRIPT
        script = Script()
        #ADD PARAMS
        self.params['userid'] = str(self.ui.lineEdit_userid.text())
        self.params['mouseid'] = str(self.ui.lineEdit_mouseid.text())
        self.params['logdir'] = str(self.ui.lineEdit_logDir.text())
        self.params['task'] = str(self.ui.lineEdit_task.text())
        self.params['stage'] = str(self.ui.lineEdit_stage.text())
        self.params['protocol'] = str(self.ui.lineEdit_foragingProtocol.text())
        self.params['nidevice'] = self.nidevice
        self.params['rewardport'] = self.rewardport
        self.params['rewardline'] = self.rewardline
        self.params['encodervsigchannel'] = self.encodervsigchannel
        self.params['encodervinchannel'] = self.encodervinchannel
        self.params['backupdir'] = self.backupdir
        self.params['syncsqr'] = self.syncsqr
        self.params['syncsqrloc'] = self.syncsqrloc

        paramstr = "params = "+repr(self.params) + "\n" + "params['script']=__file__\n"
        script.add(paramstr)
        script.add()
        
        #ADD TERRAIN
        script.add("\nterrain = Terrain(['color','orientation'])")
        for i in range(self.ui.tableWidget_terrainParams.rowCount()):
            keystr = self.ui.tableWidget_terrainParams.item(i,0)
            valstr = self.ui.tableWidget_terrainParams.item(i,1)
            if keystr is not None:
                terrainstr = 'terrain.'+keystr.text()+"="+valstr.text()
                script.add(terrainstr)

        #ADD WINDOW
        windowstr = "\nwindow = visual.Window(units='norm',monitor='"+ \
            self.monitor+"',fullscr=True,screen="+str(self.screen)+")"
        script.add(windowstr)

        #ADD BGSTIM
        script.add(self.bgStimText)

        #ADD BGSWEEPS
        script.add('bgSweep={}')
        for i in range(self.ui.tableWidget_bgStimulus.rowCount()):
            keystr = self.ui.tableWidget_bgStimulus.item(i,0)
            valstr = self.ui.tableWidget_bgStimulus.item(i,1)
            if keystr is not None:
                bgsweepstr = "bgSweep['"+keystr.text()+"']="+valstr.text()
                script.add(bgsweepstr)        

        #ADD FGSTIM
        script.add(self.fgStimText)

        #ADD FGSWEEPS
        script.add('fgSweep={}')
        for i in range(self.ui.tableWidget_fgStimulus.rowCount()):
            keystr = self.ui.tableWidget_fgStimulus.item(i,0)
            valstr = self.ui.tableWidget_fgStimulus.item(i,1)
            if keystr is not None:
                fgsweepstr = "fgSweep['"+keystr.text()+"']="+valstr.text()
                script.add(fgsweepstr)  

        #CREATE FORAGING INSTANCE
        foragingstr = "g=Foraging(window=window,terrain=terrain," + \
            "params=params,bgStim=bgStim,bgFrame=bgFrame," + \
            "bgSweep=bgSweep,fgStim=fgStim)"
        script.add(foragingstr)

        #ADD RUN()
        script.add("g.run()")

        return script

    def _preview(self):
        """Generates a preview in a small window"""
        from psychopy import visual,event,monitors,misc

        window = visual.Window(monitor = 'testMonitor')

        if self.bgStimText is not None: exec(self.bgStimText)
        if self.fgStimText is not None: exec(self.fgStimText)

        while True:
            for keys in event.getKeys(timeStamped=True):
                if keys[0]in ['escape','q']:
                    window.close()
            if self.bgStimText is not None: bgStim.draw()
            if self.fgStimText is not None: fgStim.draw()
            window.flip()            

    def _rewarddiag(self):
        if self.rewarddiag is None:
            self.rewarddiag = RewardDiagnostic()
        self.rewarddiag.show()


class RewardDiagnostic(QtGui.QWidget):
    """docstring for RewardDiagnostic"""
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
   


if __name__ == "__main__":
    #sys.path.append('/home/derricw/GitHub')  #get rid of this when I'm coding in windows
    #sys.path.append(r'C:\Users\derricw\Documents\GitHub') #comment this in windows
    app = QtGui.QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())