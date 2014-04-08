# -*- coding: utf-8 -*-
"""
Created on 4/8/14 2:14 PM 2013
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

"""

import sys
import logging
from PyQt4 import QtGui, QtCore
# try:
#     from lib.pyqtgraph import QtGui, QtCore  # ALL HAIL LUKE!
#     import lib.pyqtgraph as pg
# except ImportError:
#     pg = None


from ui.MainWindowUi import Ui_MainWindow
from pyfl593b import FL593B


class Main(QtGui.QMainWindow):
    _device_ref = None

    def __init__(self, app):
        QtGui.QMainWindow.__init__(self)
        self.app = app
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.push_REN.toggled.connect(self.toggle_output_enabled)

        self.stopwatch = QtCore.QElapsedTimer()
        self.gui_refresh_interval = 100
        QtCore.QTimer.singleShot(0, self.initialize)  # fires when event loop starts

    def initialize(self):
        """Set up device and representations once UI was initiated."""
        assert self.device is not None

        self.ui.lbl_dev_name.setText(self.device.model)
        self.ui.lbl_fw_ver.setText(self.device.fwver)

        self.ui.push_REN.setChecked(self.device.remote_enable)

        self.refresh()

    def refresh(self):
        elapsed = self.stopwatch.restart()
        self.device.update_alarms()
        self.ui.ckb_OUT.setChecked(self.device.output_enable)
        self.ui.ckb_LEN.setChecked(self.device.local_enable)
        self.ui.ckb_XEN.setChecked(self.device.external_enable)
        self.ui.push_REN.setChecked(self.device.remote_enable)

        QtCore.QTimer.singleShot(self.gui_refresh_interval, self.refresh)

    @property
    def device(self):
        """Getter for device handle."""
        if self._device_ref is None:
            try:
                self._device_ref = FL593B()
            except Exception, e:
                raise e
        else:
            return self._device_ref

    def toggle_output_enabled(self, state):
        self.device.remote_enable = state

#############################################################
def main(*args, **kwargs):
    app = QtGui.QApplication([])
    # identifiers for QSettings persistent application settings
    app.setOrganizationName('spotter_inc')
    app.setOrganizationDomain('spotter.sp')
    app.setApplicationName('Spotter')

    window = Main(app, *args, **kwargs)
    window.show()
    window.raise_()  # needed on OSX?

    sys.exit(app.exec_())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Command line parsing

    main()