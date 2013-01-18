# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mousedata.ui'
#
# Created: Wed Jan 16 17:39:59 2013
#      by: PyQt4 UI code generator 4.9.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(869, 690)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.groupBox_mouseid = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_mouseid.setGeometry(QtCore.QRect(20, 20, 281, 71))
        self.groupBox_mouseid.setObjectName(_fromUtf8("groupBox_mouseid"))
        self.lineEdit_mouseid = QtGui.QLineEdit(self.groupBox_mouseid)
        self.lineEdit_mouseid.setGeometry(QtCore.QRect(20, 30, 231, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_mouseid.setFont(font)
        self.lineEdit_mouseid.setObjectName(_fromUtf8("lineEdit_mouseid"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(320, 20, 531, 581))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.GraphTab = QtGui.QWidget()
        self.GraphTab.setObjectName(_fromUtf8("GraphTab"))
        self.mplwidget_journey = MatplotlibWidget(self.GraphTab)
        self.mplwidget_journey.setGeometry(QtCore.QRect(20, 10, 491, 241))
        self.mplwidget_journey.setObjectName(_fromUtf8("mplwidget_journey"))
        self.mplwidget_velocity = MatplotlibWidget(self.GraphTab)
        self.mplwidget_velocity.setGeometry(QtCore.QRect(20, 260, 491, 261))
        self.mplwidget_velocity.setObjectName(_fromUtf8("mplwidget_velocity"))
        self.tabWidget.addTab(self.GraphTab, _fromUtf8(""))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.tableWidget_data = QtGui.QTableWidget(self.tab)
        self.tableWidget_data.setGeometry(QtCore.QRect(20, 20, 491, 521))
        self.tableWidget_data.setRowCount(0)
        self.tableWidget_data.setObjectName(_fromUtf8("tableWidget_data"))
        self.tableWidget_data.setColumnCount(0)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.PerformanceTab = QtGui.QWidget()
        self.PerformanceTab.setObjectName(_fromUtf8("PerformanceTab"))
        self.tableWidget_performance = QtGui.QTableWidget(self.PerformanceTab)
        self.tableWidget_performance.setGeometry(QtCore.QRect(20, 20, 481, 501))
        self.tableWidget_performance.setObjectName(_fromUtf8("tableWidget_performance"))
        self.tableWidget_performance.setColumnCount(0)
        self.tableWidget_performance.setRowCount(0)
        self.tabWidget.addTab(self.PerformanceTab, _fromUtf8(""))
        self.HistoryTab = QtGui.QWidget()
        self.HistoryTab.setObjectName(_fromUtf8("HistoryTab"))
        self.tabWidget.addTab(self.HistoryTab, _fromUtf8(""))
        self.groupBox_logs = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_logs.setGeometry(QtCore.QRect(20, 110, 281, 491))
        self.groupBox_logs.setObjectName(_fromUtf8("groupBox_logs"))
        self.listWidget_logs = QtGui.QListWidget(self.groupBox_logs)
        self.listWidget_logs.setGeometry(QtCore.QRect(10, 20, 251, 451))
        self.listWidget_logs.setObjectName(_fromUtf8("listWidget_logs"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 869, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MouseData", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_mouseid.setTitle(QtGui.QApplication.translate("MainWindow", "Mouse ID", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.GraphTab), QtGui.QApplication.translate("MainWindow", "Graph", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("MainWindow", "Data", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.PerformanceTab), QtGui.QApplication.translate("MainWindow", "Performance", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.HistoryTab), QtGui.QApplication.translate("MainWindow", "History", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_logs.setTitle(QtGui.QApplication.translate("MainWindow", "Logs", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHelp.setTitle(QtGui.QApplication.translate("MainWindow", "Help", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setText(QtGui.QApplication.translate("MainWindow", "About", None, QtGui.QApplication.UnicodeUTF8))

from matplotlibwidget import MatplotlibWidget
