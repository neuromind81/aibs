'''
Created on Oct 18, 2012

@author: derricw
'''

import os
import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QObject as Qt
from mousedatalayout import Ui_MainWindow
 
class MyForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.dataDir = "C:\\ExperimentData\\"  #location of data files
        self.getMouseLogs()
        
        Qt.connect(self.ui.lineEdit_mouseid, QtCore.SIGNAL("textChanged(QString)"), self.getMouseLogs)     
        Qt.connect(self.ui.listWidget_logs, QtCore.SIGNAL("itemSelectionChanged()"),self.logSelected)


    def populateLogList(self, logs):
        """ Adds logs to listWidget_logs """
        self.ui.listWidget_logs.clear()
        self.ui.listWidget_logs.addItems(logs)
        
    def getMouseLogs(self):
        """ Gets logs for particular mouse. Populates log list is possible. """
        mouseid = self.ui.lineEdit_mouseid.text()
        path = os.path.join(self.dataDir, str(mouseid))
        try:
            files = os.listdir(path)
            self.populateLogList(files)
        except:
            pass
        
    def logSelected(self):
        """ Callback for when a mouse log or mouse folder is selected """
        # check to see if selection is a directory or file
        
        # read selected file or files
        selection = self.ui.listWidget_logs.selectedItems() #returns QListWidget object
        for s in selection:
            if os.path.exists(os.path.join(self.dataDir, str(s.text()))):
                self.ui.lineEdit_mouseid.setText(s.text())
            else:
                self.populateDataView()
                
    def populateDataView(self):
        """ Populates GraphTab, PerformanceTab """
        path = os.path.join(os.path.join(self.dataDir, str(self.ui.lineEdit_mouseid.text())), 
                       str(self.ui.listWidget_logs.selectedItems()[0].text()))
        f = open(path, 'r')
        for rl in f.readlines():
            pass #add to table
 
 
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())