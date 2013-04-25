'''
Created on Oct 18, 2012

@author: derricw
'''

 
import sys
from PyQt4 import QtCore, QtGui
from EyetrackerLayout import Ui_MainWindow

from Eyetracker import Eyetracker
 
class MyForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        #Connect signals
        self.ui.horizontalSlider_general_blur.sliderMoved.connect(self._blurSlider)
        self.ui.horizontalSlider_general_zoom.sliderMoved.connect(self._zoomSlider)
        self.ui.horizontalSlider_led_binary.sliderMoved.connect(self._ledBinarySlider)
        self.ui.horizontalSlider_led_min.sliderMoved.connect(self._ledMinSlider)
        self.ui.horizontalSlider_led_max.sliderMoved.connect(self._ledMaxSlider)
        self.ui.horizontalSlider_pupil_binary.sliderMoved.connect(self._pupilBinarySlider)
        self.ui.horizontalSlider_pupil_min.sliderMoved.connect(self._pupilMinSlider)
        self.ui.horizontalSlider_pupil_max.sliderMoved.connect(self._pupilMaxSlider)
        

        #Create Eyetracker
        self.et = Eyetracker()

        #Set initial slider bar states (might should be before signals)
        self.ui.horizontalSlider_general_blur.setValue(self.et.blur)
        self.ui.horizontalSlider_general_zoom.setValue(self.et.zoom)
        self.ui.horizontalSlider_led_binary.setValue(self.et.ledthresh)
        self.ui.horizontalSlider_led_min.setValue(self.et.ledsize[0])
        self.ui.horizontalSlider_led_max.setValue(self.et.ledsize[1])
        self.ui.horizontalSlider_pupil_binary.setValue(self.et.pupilthresh)
        self.ui.horizontalSlider_pupil_min.setValue(self.et.pupilsize[0])
        self.ui.horizontalSlider_pupil_max.setValue(self.et.pupilsize[1])

        #Timer setup
        self.ctimer = QtCore.QTimer()
        self.ctimer.timeout.connect(self._tick)
        self.ctimer.start(1)


    def _blurSlider(self):
        self.et.blur = int(self.ui.horizontalSlider_general_blur.value())

    def _zoomSlider(self):
        self.et.zoom = int(self.ui.horizontalSlider_general_zoom.value())

    def _ledBinarySlider(self):
        self.et.ledthresh = int(self.ui.horizontalSlider_led_binary.value())

    def _ledMinSlider(self):
        newval = int(self.ui.horizontalSlider_led_min.value())
        if newval <= self.et.ledsize[1]:
            self.et.ledsize[0] = newval

    def _ledMaxSlider(self):
        newval = int(self.ui.horizontalSlider_led_max.value())
        if newval >= self.et.ledsize[0]:
            self.et.ledsize[1] = newval

    def _pupilBinarySlider(self):
        self.et.pupilthresh = int(self.ui.horizontalSlider_pupil_binary.value())

    def _pupilMinSlider(self):
        newval = int(self.ui.horizontalSlider_pupil_min.value())
        if newval <= self.et.pupilsize[1]:
            self.et.pupilsize[0] = newval

    def _pupilMaxSlider(self):
        newval = int(self.ui.horizontalSlider_pupil_max.value())
        if newval >= self.et.pupilsize[0]:
            self.et.pupilsize[1] = newval

    def _tick(self):
        self.et.nextFrame()

    def closeEvent(self,evnt):
        self.ctimer.stop()
        self.et.close()
        print "CLOSING..."

 

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())