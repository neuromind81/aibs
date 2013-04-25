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

        #Timer setup
        self.ctimer = QtCore.QTimer()
        self.ctimer.timeout.connect(self._tick)
        self.ctimer.start(1)


    def _blurSlider(self):
        self.et.blur = int(self.ui.horizontalSlider_general_blur.value())

    def _zoomSlider(self):
        pass

    def _ledBinarySlider(self):
        pass

    def _ledMinSlider(self):
        pass

    def _ledMaxSlider(self):
        pass

    def _pupilBinarySlider(self):
        pass

    def _pupilMinSlider(self):
        pass

    def _pupilMaxSlider(self):
        pass

    def _tick(self):
        self.et.nextFrame()


 
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())