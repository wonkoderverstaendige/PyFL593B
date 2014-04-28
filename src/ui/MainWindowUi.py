# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindowUi.ui'
#
# Created: Mon Apr 28 06:29:46 2014
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
        MainWindow.resize(402, 480)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.layout_channels = QtGui.QHBoxLayout()
        self.layout_channels.setObjectName(_fromUtf8("layout_channels"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.layout_channels.addItem(spacerItem)
        self.gridLayout.addLayout(self.layout_channels, 0, 0, 1, 2)
        self.groupBox_3 = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setMargin(0)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.gridLayout_4 = QtGui.QGridLayout()
        self.gridLayout_4.setVerticalSpacing(0)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.push_REN = QtGui.QPushButton(self.groupBox_3)
        self.push_REN.setCheckable(True)
        self.push_REN.setObjectName(_fromUtf8("push_REN"))
        self.gridLayout_4.addWidget(self.push_REN, 0, 4, 1, 1)
        self.label = QtGui.QLabel(self.groupBox_3)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_4.addWidget(self.label, 0, 0, 1, 1)
        self.lbl_fw_ver = QtGui.QLabel(self.groupBox_3)
        self.lbl_fw_ver.setObjectName(_fromUtf8("lbl_fw_ver"))
        self.gridLayout_4.addWidget(self.lbl_fw_ver, 1, 1, 1, 1)
        self.lbl_dev_name = QtGui.QLabel(self.groupBox_3)
        self.lbl_dev_name.setObjectName(_fromUtf8("lbl_dev_name"))
        self.gridLayout_4.addWidget(self.lbl_dev_name, 0, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem1, 0, 2, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox_3)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_4.addWidget(self.label_2, 1, 0, 1, 1)
        self.ckb_XEN = QtGui.QCheckBox(self.groupBox_3)
        self.ckb_XEN.setEnabled(False)
        self.ckb_XEN.setCheckable(True)
        self.ckb_XEN.setObjectName(_fromUtf8("ckb_XEN"))
        self.gridLayout_4.addWidget(self.ckb_XEN, 1, 3, 1, 1)
        self.ckb_LEN = QtGui.QCheckBox(self.groupBox_3)
        self.ckb_LEN.setEnabled(False)
        self.ckb_LEN.setCheckable(True)
        self.ckb_LEN.setObjectName(_fromUtf8("ckb_LEN"))
        self.gridLayout_4.addWidget(self.ckb_LEN, 1, 4, 1, 1)
        self.ckb_OUT = QtGui.QCheckBox(self.groupBox_3)
        self.ckb_OUT.setEnabled(False)
        self.ckb_OUT.setObjectName(_fromUtf8("ckb_OUT"))
        self.gridLayout_4.addWidget(self.ckb_OUT, 0, 3, 1, 1)
        self.lbl_fps = QtGui.QLabel(self.groupBox_3)
        self.lbl_fps.setObjectName(_fromUtf8("lbl_fps"))
        self.gridLayout_4.addWidget(self.lbl_fps, 2, 4, 1, 1)
        self.lbl_debug = QtGui.QLabel(self.groupBox_3)
        self.lbl_debug.setObjectName(_fromUtf8("lbl_debug"))
        self.gridLayout_4.addWidget(self.lbl_debug, 2, 0, 1, 1)
        self.lbl_debug2 = QtGui.QLabel(self.groupBox_3)
        self.lbl_debug2.setObjectName(_fromUtf8("lbl_debug2"))
        self.gridLayout_4.addWidget(self.lbl_debug2, 2, 1, 1, 1)
        self.horizontalLayout_3.addLayout(self.gridLayout_4)
        self.gridLayout.addWidget(self.groupBox_3, 1, 0, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 402, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuDevice = QtGui.QMenu(self.menubar)
        self.menuDevice.setObjectName(_fromUtf8("menuDevice"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
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
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.groupBox_3.setTitle(_translate("MainWindow", "Status", None))
        self.push_REN.setText(_translate("MainWindow", "Remote Enable", None))
        self.label.setText(_translate("MainWindow", "Device Name:", None))
        self.lbl_fw_ver.setText(_translate("MainWindow", "NO_CONN", None))
        self.lbl_dev_name.setText(_translate("MainWindow", "NO_CONN", None))
        self.label_2.setText(_translate("MainWindow", "Firmware version:", None))
        self.ckb_XEN.setText(_translate("MainWindow", "External", None))
        self.ckb_LEN.setText(_translate("MainWindow", "Local", None))
        self.ckb_OUT.setText(_translate("MainWindow", "Output", None))
        self.lbl_fps.setText(_translate("MainWindow", "TextLabel", None))
        self.lbl_debug.setText(_translate("MainWindow", "TextLabel", None))
        self.lbl_debug2.setText(_translate("MainWindow", "TextLabel", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuDevice.setTitle(_translate("MainWindow", "Device", None))
        self.actionQuit.setText(_translate("MainWindow", "Quit", None))
        self.actionQuit.setShortcut(_translate("MainWindow", "Ctrl+Q", None))
        self.actionReset.setText(_translate("MainWindow", "Reset", None))

