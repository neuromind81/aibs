# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'rewarddiag.ui'
#
# Created: Thu Apr 18 16:48:30 2013
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(562, 157)
        self.pushButton_dispense = QtGui.QPushButton(Form)
        self.pushButton_dispense.setGeometry(QtCore.QRect(250, 30, 131, 91))
        self.pushButton_dispense.setObjectName(_fromUtf8("pushButton_dispense"))
        self.pushButton_calibrate = QtGui.QPushButton(Form)
        self.pushButton_calibrate.setGeometry(QtCore.QRect(400, 30, 131, 91))
        self.pushButton_calibrate.setObjectName(_fromUtf8("pushButton_calibrate"))
        self.groupBox_volume = QtGui.QGroupBox(Form)
        self.groupBox_volume.setGeometry(QtCore.QRect(30, 30, 191, 91))
        self.groupBox_volume.setObjectName(_fromUtf8("groupBox_volume"))
        self.lineEdit_volume = QtGui.QLineEdit(self.groupBox_volume)
        self.lineEdit_volume.setGeometry(QtCore.QRect(40, 20, 121, 25))
        self.lineEdit_volume.setObjectName(_fromUtf8("lineEdit_volume"))
        self.comboBox_unit = QtGui.QComboBox(self.groupBox_volume)
        self.comboBox_unit.setGeometry(QtCore.QRect(60, 50, 82, 25))
        self.comboBox_unit.setObjectName(_fromUtf8("comboBox_unit"))
        self.comboBox_unit.addItem(_fromUtf8(""))
        self.comboBox_unit.addItem(_fromUtf8(""))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Reward Diagnostics", None))
        self.pushButton_dispense.setText(_translate("Form", "Dispense", None))
        self.pushButton_calibrate.setText(_translate("Form", "Calibrate", None))
        self.groupBox_volume.setTitle(_translate("Form", "Volume/Time", None))
        self.comboBox_unit.setItemText(0, _translate("Form", "uL", None))
        self.comboBox_unit.setItemText(1, _translate("Form", "sec", None))

