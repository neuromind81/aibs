'''
Created on Oct 18, 2012

@author: derricw

Displays a GUI for adjusting camera parameters and thresholds for pruning out the LED
    and pupil on an Eyetracker object instance.

'''

 
import sys
import os
from PyQt4 import QtCore, QtGui
from EyetrackerLayout import Ui_MainWindow

from Eyetracker import Eyetracker
 
class MyForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #ETC
        self.output = False
        
        #Connect signals
        self.ui.horizontalSlider_general_blur.sliderMoved.connect(self._blurSlider)
        self.ui.horizontalSlider_general_zoom.sliderMoved.connect(self._zoomSlider)
        self.ui.horizontalSlider_led_binary.sliderMoved.connect(self._ledBinarySlider)
        self.ui.horizontalSlider_led_min.sliderMoved.connect(self._ledMinSlider)
        self.ui.horizontalSlider_led_max.sliderMoved.connect(self._ledMaxSlider)
        self.ui.horizontalSlider_pupil_binary.sliderMoved.connect(self._pupilBinarySlider)
        self.ui.horizontalSlider_pupil_min.sliderMoved.connect(self._pupilMinSlider)
        self.ui.horizontalSlider_pupil_max.sliderMoved.connect(self._pupilMaxSlider)
        self.ui.horizontalSlider_camera_hue.sliderMoved.connect(self._cameraHueSlider)
        self.ui.horizontalSlider_camera_saturation.sliderMoved.connect(self._cameraSaturationSlider)
        self.ui.horizontalSlider_camera_brightness.sliderMoved.connect(self._cameraBrightnessSlider)
        self.ui.horizontalSlider_camera_gain.sliderMoved.connect(self._cameraGainSlider)
        self.ui.horizontalSlider_camera_contrast.sliderMoved.connect(self._cameraContrastSlider)
        self.ui.horizontalSlider_camera_exposure.sliderMoved.connect(self._cameraExposureSlider)
        self.ui.pushButton_output.clicked.connect(self._outputToggle)

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

        #and for the camera...
        #self.ui.horizontalSlider_camera_hue.setValue(
        #    self.et.camproperties['hue'])
        self.ui.horizontalSlider_camera_saturation.setValue(
            self.et.camproperties['saturation'])
        self.ui.horizontalSlider_camera_brightness.setValue(
            self.et.camproperties['brightness'])
        #self.ui.horizontalSlider_camera_gain.setValue(
        #    self.et.camproperties['gain'])
        self.ui.horizontalSlider_camera_contrast.setValue(
            self.et.camproperties['contrast'])
        self.ui.horizontalSlider_camera_exposure.setValue(
            self.et.camproperties['exposure'])

        #Timer setup
        self.ctimer = QtCore.QTimer()
        self.ctimer.timeout.connect(self._tick)
        self.ctimer.start(1) #run as fast as possible


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

    def _cameraHueSlider(self):
        pass

    def _cameraSaturationSlider(self):
        self.et.camproperties['saturation'] = int(
            self.ui.horizontalSlider_camera_saturation.value())
        self.et.setCamProp('saturation')

    def _cameraBrightnessSlider(self):
        self.et.camproperties['brightness'] = int(
            self.ui.horizontalSlider_camera_brightness.value())
        self.et.setCamProp('brightness')

    def _cameraGainSlider(self):
        pass

    def _cameraContrastSlider(self):
        self.et.camproperties['contrast'] = int(
            self.ui.horizontalSlider_camera_contrast.value())
        self.et.setCamProp('contrast')

    def _cameraExposureSlider(self):
        self.et.camproperties['exposure'] = int(
            self.ui.horizontalSlider_camera_exposure.value())
        self.et.setCamProp('exposure')

    def _tick(self):
        try:
            self.et.nextFrame()
            if self.output:
                self._output()
        except:
            self.et.getNewCam()

    def _output(self):
        if self.ui.checkBox_toFile.isChecked():
            out = str(self.et.getGaze())+'\n'
            self.outputfile.write(out)
        if self.ui.checkBox_toVideo.isChecked():
            pass #grabs frames automatically
        if self.ui.checkBox_toConsole.isChecked():
            print self.et.getGaze()

    def _outputToggle(self):
        if self.output:
            self.output=False
            try:
                self.outputfile.close()
            except Exception, e:
                pass
            try:
                self.et.stopVideo()
            except Exception, e:
                print e
        else:
            if self.ui.checkBox_toFile.isChecked():
                outdir = str(self.ui.lineEdit_output.text())
                self.outputfile = open(outdir,'w+')
            if self.ui.checkBox_toVideo.isChecked():
                self.et.startVideo(str(self.ui.lineEdit_video.text()))
            self.output=True

    def closeEvent(self,evnt):
        self.ctimer.stop()
        self.et.close()
        print "CLOSING..."

 
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())