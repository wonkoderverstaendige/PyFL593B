# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindowUi.ui'
#
# Created: Thu Aug 14 03:02:55 2014
#      by: PyQt4 UI code generator 4.10.4
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
        MainWindow.resize(456, 480)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/laser_warning.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setMargin(1)
        self.gridLayout.setSpacing(1)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.frame = QtGui.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.frame_layout = QtGui.QVBoxLayout()
        self.frame_layout.setObjectName(_fromUtf8("frame_layout"))
        self.verticalLayout.addLayout(self.frame_layout)
        self.gridLayout.addWidget(self.frame, 1, 1, 1, 2)
        self.layout_channels = QtGui.QHBoxLayout()
        self.layout_channels.setObjectName(_fromUtf8("layout_channels"))
        self.gridLayout.addLayout(self.layout_channels, 0, 1, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 456, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuDevice = QtGui.QMenu(self.menubar)
        self.menuDevice.setObjectName(_fromUtf8("menuDevice"))
        MainWindow.setMenuBar(self.menubar)
        self.actionQuit = QtGui.QAction(MainWindow)
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.actionReset = QtGui.QAction(MainWindow)
        self.actionReset.setObjectName(_fromUtf8("actionReset"))
        self.menuFile.addAction(self.actionQuit)
        self.menuDevice.addAction(self.actionReset)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuDevice.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "FL593FL", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuDevice.setTitle(_translate("MainWindow", "Device", None))
        self.actionQuit.setText(_translate("MainWindow", "Quit", None))
        self.actionQuit.setShortcut(_translate("MainWindow", "Ctrl+Q", None))
        self.actionReset.setText(_translate("MainWindow", "Reset", None))

import icons_rc
