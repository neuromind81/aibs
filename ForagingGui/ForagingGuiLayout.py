# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created: Tue Apr 02 14:17:52 2013
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(885, 847)
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.groupBox_mouse = QtGui.QGroupBox(self.centralWidget)
        self.groupBox_mouse.setGeometry(QtCore.QRect(20, 10, 411, 301))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_mouse.setFont(font)
        self.groupBox_mouse.setObjectName(_fromUtf8("groupBox_mouse"))
        self.lineEdit_mouseid = QtGui.QLineEdit(self.groupBox_mouse)
        self.lineEdit_mouseid.setGeometry(QtCore.QRect(30, 30, 191, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit_mouseid.setFont(font)
        self.lineEdit_mouseid.setObjectName(_fromUtf8("lineEdit_mouseid"))
        self.pushButton_sessionPerformance = QtGui.QPushButton(self.groupBox_mouse)
        self.pushButton_sessionPerformance.setGeometry(QtCore.QRect(20, 250, 171, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_sessionPerformance.setFont(font)
        self.pushButton_sessionPerformance.setObjectName(_fromUtf8("pushButton_sessionPerformance"))
        self.pushButton_lifetimePerformance = QtGui.QPushButton(self.groupBox_mouse)
        self.pushButton_lifetimePerformance.setGeometry(QtCore.QRect(210, 250, 161, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_lifetimePerformance.setFont(font)
        self.pushButton_lifetimePerformance.setObjectName(_fromUtf8("pushButton_lifetimePerformance"))
        self.groupBox_4 = QtGui.QGroupBox(self.groupBox_mouse)
        self.groupBox_4.setGeometry(QtCore.QRect(10, 50, 391, 191))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.groupBox_4.setFont(font)
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.tableWidget_mouse = QtGui.QTableWidget(self.groupBox_4)
        self.tableWidget_mouse.setGeometry(QtCore.QRect(10, 20, 371, 161))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.tableWidget_mouse.setFont(font)
        self.tableWidget_mouse.setRowCount(10)
        self.tableWidget_mouse.setColumnCount(2)
        self.tableWidget_mouse.setObjectName(_fromUtf8("tableWidget_mouse"))
        self.tableWidget_mouse.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget_mouse.horizontalHeader().setDefaultSectionSize(150)
        self.tableWidget_mouse.horizontalHeader().setMinimumSectionSize(26)
        self.groupBox_BGStimulus = QtGui.QGroupBox(self.centralWidget)
        self.groupBox_BGStimulus.setGeometry(QtCore.QRect(20, 550, 411, 251))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_BGStimulus.setFont(font)
        self.groupBox_BGStimulus.setObjectName(_fromUtf8("groupBox_BGStimulus"))
        self.pushButton_loadBGStimulus = QtGui.QPushButton(self.groupBox_BGStimulus)
        self.pushButton_loadBGStimulus.setGeometry(QtCore.QRect(320, 10, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_loadBGStimulus.setFont(font)
        self.pushButton_loadBGStimulus.setObjectName(_fromUtf8("pushButton_loadBGStimulus"))
        self.groupBox_3 = QtGui.QGroupBox(self.groupBox_BGStimulus)
        self.groupBox_3.setGeometry(QtCore.QRect(10, 40, 391, 201))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.groupBox_3.setFont(font)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.tableWidget_BGStimulus = QtGui.QTableWidget(self.groupBox_3)
        self.tableWidget_BGStimulus.setGeometry(QtCore.QRect(10, 20, 371, 161))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.tableWidget_BGStimulus.setFont(font)
        self.tableWidget_BGStimulus.setRowCount(10)
        self.tableWidget_BGStimulus.setColumnCount(2)
        self.tableWidget_BGStimulus.setObjectName(_fromUtf8("tableWidget_BGStimulus"))
        self.tableWidget_BGStimulus.horizontalHeader().setDefaultSectionSize(150)
        self.pushButton_saveBGStimulus = QtGui.QPushButton(self.groupBox_BGStimulus)
        self.pushButton_saveBGStimulus.setGeometry(QtCore.QRect(230, 10, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_saveBGStimulus.setFont(font)
        self.pushButton_saveBGStimulus.setObjectName(_fromUtf8("pushButton_saveBGStimulus"))
        self.groupBox_foraging = QtGui.QGroupBox(self.centralWidget)
        self.groupBox_foraging.setGeometry(QtCore.QRect(440, 10, 431, 781))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_foraging.setFont(font)
        self.groupBox_foraging.setObjectName(_fromUtf8("groupBox_foraging"))
        self.pushButton_run = QtGui.QPushButton(self.groupBox_foraging)
        self.pushButton_run.setGeometry(QtCore.QRect(260, 0, 151, 51))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_run.setFont(font)
        self.pushButton_run.setStyleSheet(_fromUtf8("background-color: rgb(255, 170, 0);"))
        self.pushButton_run.setObjectName(_fromUtf8("pushButton_run"))
        self.label_2 = QtGui.QLabel(self.groupBox_foraging)
        self.label_2.setGeometry(QtCore.QRect(20, 70, 46, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.lineEdit_logDir = QtGui.QLineEdit(self.groupBox_foraging)
        self.lineEdit_logDir.setGeometry(QtCore.QRect(80, 70, 321, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit_logDir.setFont(font)
        self.lineEdit_logDir.setObjectName(_fromUtf8("lineEdit_logDir"))
        self.label_3 = QtGui.QLabel(self.groupBox_foraging)
        self.label_3.setGeometry(QtCore.QRect(20, 110, 41, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.lineEdit_task = QtGui.QLineEdit(self.groupBox_foraging)
        self.lineEdit_task.setGeometry(QtCore.QRect(80, 110, 321, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit_task.setFont(font)
        self.lineEdit_task.setObjectName(_fromUtf8("lineEdit_task"))
        self.lineEdit_stage = QtGui.QLineEdit(self.groupBox_foraging)
        self.lineEdit_stage.setGeometry(QtCore.QRect(80, 150, 321, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit_stage.setFont(font)
        self.lineEdit_stage.setObjectName(_fromUtf8("lineEdit_stage"))
        self.label_4 = QtGui.QLabel(self.groupBox_foraging)
        self.label_4.setGeometry(QtCore.QRect(20, 150, 41, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_4.setFont(font)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.pushButton_loadProtocol = QtGui.QPushButton(self.groupBox_foraging)
        self.pushButton_loadProtocol.setGeometry(QtCore.QRect(260, 190, 141, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_loadProtocol.setFont(font)
        self.pushButton_loadProtocol.setObjectName(_fromUtf8("pushButton_loadProtocol"))
        self.pushButton_protocolEditor = QtGui.QPushButton(self.groupBox_foraging)
        self.pushButton_protocolEditor.setGeometry(QtCore.QRect(100, 190, 141, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_protocolEditor.setFont(font)
        self.pushButton_protocolEditor.setObjectName(_fromUtf8("pushButton_protocolEditor"))
        self.label_5 = QtGui.QLabel(self.groupBox_foraging)
        self.label_5.setGeometry(QtCore.QRect(20, 250, 101, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_5.setFont(font)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.lineEdit_foragingProtocol = QtGui.QLineEdit(self.groupBox_foraging)
        self.lineEdit_foragingProtocol.setGeometry(QtCore.QRect(140, 250, 261, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit_foragingProtocol.setFont(font)
        self.lineEdit_foragingProtocol.setObjectName(_fromUtf8("lineEdit_foragingProtocol"))
        self.pushButton_displayTerrain = QtGui.QPushButton(self.groupBox_foraging)
        self.pushButton_displayTerrain.setGeometry(QtCore.QRect(150, 710, 131, 51))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_displayTerrain.setFont(font)
        self.pushButton_displayTerrain.setObjectName(_fromUtf8("pushButton_displayTerrain"))
        self.pushButton_rewardDiagnostic = QtGui.QPushButton(self.groupBox_foraging)
        self.pushButton_rewardDiagnostic.setGeometry(QtCore.QRect(290, 710, 131, 51))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_rewardDiagnostic.setFont(font)
        self.pushButton_rewardDiagnostic.setObjectName(_fromUtf8("pushButton_rewardDiagnostic"))
        self.pushButton_TBD = QtGui.QPushButton(self.groupBox_foraging)
        self.pushButton_TBD.setGeometry(QtCore.QRect(10, 710, 131, 51))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_TBD.setFont(font)
        self.pushButton_TBD.setObjectName(_fromUtf8("pushButton_TBD"))
        self.groupBox_FGStimulus = QtGui.QGroupBox(self.groupBox_foraging)
        self.groupBox_FGStimulus.setGeometry(QtCore.QRect(10, 490, 411, 211))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_FGStimulus.setFont(font)
        self.groupBox_FGStimulus.setObjectName(_fromUtf8("groupBox_FGStimulus"))
        self.tableWidget_FGStimulus = QtGui.QTableWidget(self.groupBox_FGStimulus)
        self.tableWidget_FGStimulus.setGeometry(QtCore.QRect(10, 50, 391, 151))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.tableWidget_FGStimulus.setFont(font)
        self.tableWidget_FGStimulus.setRowCount(10)
        self.tableWidget_FGStimulus.setColumnCount(2)
        self.tableWidget_FGStimulus.setObjectName(_fromUtf8("tableWidget_FGStimulus"))
        self.tableWidget_FGStimulus.horizontalHeader().setDefaultSectionSize(160)
        self.pushButton_loadFGStimulus = QtGui.QPushButton(self.groupBox_FGStimulus)
        self.pushButton_loadFGStimulus.setGeometry(QtCore.QRect(320, 10, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_loadFGStimulus.setFont(font)
        self.pushButton_loadFGStimulus.setObjectName(_fromUtf8("pushButton_loadFGStimulus"))
        self.pushButton_saveFGStimulus = QtGui.QPushButton(self.groupBox_FGStimulus)
        self.pushButton_saveFGStimulus.setGeometry(QtCore.QRect(230, 10, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_saveFGStimulus.setFont(font)
        self.pushButton_saveFGStimulus.setObjectName(_fromUtf8("pushButton_saveFGStimulus"))
        self.groupBox_terrain = QtGui.QGroupBox(self.groupBox_foraging)
        self.groupBox_terrain.setGeometry(QtCore.QRect(10, 280, 411, 211))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_terrain.setFont(font)
        self.groupBox_terrain.setObjectName(_fromUtf8("groupBox_terrain"))
        self.tableWidget_terrain = QtGui.QTableWidget(self.groupBox_terrain)
        self.tableWidget_terrain.setGeometry(QtCore.QRect(10, 50, 391, 151))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.tableWidget_terrain.setFont(font)
        self.tableWidget_terrain.setRowCount(20)
        self.tableWidget_terrain.setColumnCount(2)
        self.tableWidget_terrain.setObjectName(_fromUtf8("tableWidget_terrain"))
        self.tableWidget_terrain.horizontalHeader().setDefaultSectionSize(160)
        self.pushButton_loadTerrain = QtGui.QPushButton(self.groupBox_terrain)
        self.pushButton_loadTerrain.setGeometry(QtCore.QRect(320, 10, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_loadTerrain.setFont(font)
        self.pushButton_loadTerrain.setObjectName(_fromUtf8("pushButton_loadTerrain"))
        self.pushButton_saveTerrain = QtGui.QPushButton(self.groupBox_terrain)
        self.pushButton_saveTerrain.setGeometry(QtCore.QRect(230, 10, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_saveTerrain.setFont(font)
        self.pushButton_saveTerrain.setObjectName(_fromUtf8("pushButton_saveTerrain"))
        self.groupBox_experiment = QtGui.QGroupBox(self.centralWidget)
        self.groupBox_experiment.setGeometry(QtCore.QRect(20, 310, 411, 241))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_experiment.setFont(font)
        self.groupBox_experiment.setObjectName(_fromUtf8("groupBox_experiment"))
        self.pushButton_loadExperiment = QtGui.QPushButton(self.groupBox_experiment)
        self.pushButton_loadExperiment.setGeometry(QtCore.QRect(320, 10, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_loadExperiment.setFont(font)
        self.pushButton_loadExperiment.setObjectName(_fromUtf8("pushButton_loadExperiment"))
        self.groupBox_5 = QtGui.QGroupBox(self.groupBox_experiment)
        self.groupBox_5.setGeometry(QtCore.QRect(10, 40, 391, 191))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.groupBox_5.setFont(font)
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.tableWidget_experiment = QtGui.QTableWidget(self.groupBox_5)
        self.tableWidget_experiment.setGeometry(QtCore.QRect(10, 20, 371, 161))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.tableWidget_experiment.setFont(font)
        self.tableWidget_experiment.setRowCount(20)
        self.tableWidget_experiment.setColumnCount(2)
        self.tableWidget_experiment.setObjectName(_fromUtf8("tableWidget_experiment"))
        self.tableWidget_experiment.horizontalHeader().setDefaultSectionSize(150)
        self.pushButton_saveExperiment = QtGui.QPushButton(self.groupBox_experiment)
        self.pushButton_saveExperiment.setGeometry(QtCore.QRect(230, 10, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_saveExperiment.setFont(font)
        self.pushButton_saveExperiment.setObjectName(_fromUtf8("pushButton_saveExperiment"))
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtGui.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 885, 21))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))
        self.menuFiles = QtGui.QMenu(self.menuBar)
        self.menuFiles.setObjectName(_fromUtf8("menuFiles"))
        self.menuHelp = QtGui.QMenu(self.menuBar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtGui.QToolBar(MainWindow)
        self.mainToolBar.setObjectName(_fromUtf8("mainToolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtGui.QStatusBar(MainWindow)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        MainWindow.setStatusBar(self.statusBar)
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.menuHelp.addAction(self.actionAbout)
        self.menuBar.addAction(self.menuFiles.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Foraging", None))
        self.groupBox_mouse.setTitle(_translate("MainWindow", "Mouse", None))
        self.pushButton_sessionPerformance.setText(_translate("MainWindow", "Session Performance", None))
        self.pushButton_lifetimePerformance.setText(_translate("MainWindow", "Lifetime Performance", None))
        self.groupBox_4.setTitle(_translate("MainWindow", "Logs", None))
        self.groupBox_BGStimulus.setTitle(_translate("MainWindow", "Background Stimulus", None))
        self.pushButton_loadBGStimulus.setText(_translate("MainWindow", "Load", None))
        self.groupBox_3.setTitle(_translate("MainWindow", "Parameters", None))
        self.pushButton_saveBGStimulus.setText(_translate("MainWindow", "Save", None))
        self.groupBox_foraging.setTitle(_translate("MainWindow", "Foraging", None))
        self.pushButton_run.setText(_translate("MainWindow", "RUN", None))
        self.label_2.setText(_translate("MainWindow", "Log dir:", None))
        self.lineEdit_logDir.setText(_translate("MainWindow", "C:\\", None))
        self.label_3.setText(_translate("MainWindow", "Task:", None))
        self.label_4.setText(_translate("MainWindow", "Stage:", None))
        self.pushButton_loadProtocol.setText(_translate("MainWindow", "Load Protocol", None))
        self.pushButton_protocolEditor.setText(_translate("MainWindow", "Protocol Editor", None))
        self.label_5.setText(_translate("MainWindow", "Foraging Protocol:", None))
        self.pushButton_displayTerrain.setText(_translate("MainWindow", "Display Terrain", None))
        self.pushButton_rewardDiagnostic.setText(_translate("MainWindow", "Reward Diagnostic", None))
        self.pushButton_TBD.setText(_translate("MainWindow", "TBD", None))
        self.groupBox_FGStimulus.setTitle(_translate("MainWindow", "Target Stimulus", None))
        self.pushButton_loadFGStimulus.setText(_translate("MainWindow", "Load", None))
        self.pushButton_saveFGStimulus.setText(_translate("MainWindow", "Save", None))
        self.groupBox_terrain.setTitle(_translate("MainWindow", "Terrain Parameters", None))
        self.pushButton_loadTerrain.setText(_translate("MainWindow", "Load", None))
        self.pushButton_saveTerrain.setText(_translate("MainWindow", "Save", None))
        self.groupBox_experiment.setTitle(_translate("MainWindow", "Experiment Params", None))
        self.pushButton_loadExperiment.setText(_translate("MainWindow", "Load", None))
        self.groupBox_5.setTitle(_translate("MainWindow", "Parameters", None))
        self.pushButton_saveExperiment.setText(_translate("MainWindow", "Save", None))
        self.menuFiles.setTitle(_translate("MainWindow", "File", None))
        self.menuHelp.setTitle(_translate("MainWindow", "Help", None))
        self.actionAbout.setText(_translate("MainWindow", "About", None))

