'''
Created on Oct 18, 2012

@author: derricw
'''

 
import sys
from PyQt4 import QtCore as qt, QtGui
from ForagingGuiLayout import Ui_MainWindow
 
class MyForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.logDir = "C:\\BehaviorLogs\\"        
        
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
 
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())