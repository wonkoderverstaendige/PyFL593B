#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 4/8/14 2:14 PM 2013
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

"""

import sys
if sys.hexversion > 0x03000000:
    raise EnvironmentError('Python 3 not supported.')

import logging
from PyQt4 import QtGui, QtCore
from ui import MainWindowUi
from ui.StatusWidget import StatusWidget
from ui.ChannelWidget import ChannelWidget
from core.fl593fl import FL593FL

__version__ = '0.1'
LOG_LEVEL = logging.INFO
NO_EXIT_CONFIRMATION = False


class Main(QtGui.QMainWindow):
    _device_ref = None

    def __init__(self, app, *args, **kwargs):
        QtGui.QMainWindow.__init__(self)
        self.log = logging.getLogger(__name__)
        self.app = app
        self.ui = MainWindowUi.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.actionReset.triggered.connect(self.reset_device)
        self.ui.actionQuit.triggered.connect(self.close)

        # Channel widgets
        self.channel_widgets = []

        # Status widget
        self.status_widget = StatusWidget(self)
        self.ui.frame_layout.addWidget(self.status_widget)

        self.stopwatch = QtCore.QElapsedTimer()
        self.stopwatch.start()
        self.gui_refresh_interval = 0
        self.elapsed = self.gui_refresh_interval if self.gui_refresh_interval > 0 else 30
        QtCore.QTimer.singleShot(0, self.initialize)  # fires when event loop starts

    def initialize(self):
        """Set up device and representations once UI was initiated."""
        self.log.debug("Initializing...")

        if self._device_ref is None:
            try:
                self._device_ref = FL593FL()
            except Exception, e:
                raise e
        assert self.device is not None

        # add channels/initialize widgets now that we have a working connection
        self.status_widget.initialize()
        self.channel_widgets = [ChannelWidget(self, n+1) for n in range(self.device.channel_count)]
        for widget in self.channel_widgets:
            self.ui.layout_channels.addWidget(widget)
            widget.initialize(self.device.channels[widget.num_channel])

        # start main refresh loop
        self.refresh()

    def refresh(self):
        """Main loop processing/updating."""

        # update rate display (smoothed)
        self.elapsed = 0.8*self.elapsed + 0.2*self.stopwatch.restart()
        self.status_widget.set_fps(self.elapsed)

        # have the device update itself fully
        self.device.update()

        # Refresh widgets
        self.status_widget.refresh()
        for widget in self.channel_widgets:
            widget.refresh()

        # start timer for next refresh
        QtCore.QTimer.singleShot(self.gui_refresh_interval, self.refresh)

    @property
    def device(self):
        """Getter for device handle."""
        return self._device_ref

    def reset_device(self):
        """Reset device (bus). """
        self.device.reset()

    def closeEvent(self, event):
        """This party sucks. The moment I find my pants I'm out of here!"""
        if NO_EXIT_CONFIRMATION:
            reply = QtGui.QMessageBox.Yes
        else:
            reply = QtGui.QMessageBox.question(self, 'Exiting...', 'Are you sure?',
                                               QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            if self.device is not None:
                self.device.close()
            event.accept()
        else:
            event.ignore()


#############################################################
def main(*args, **kwargs):
    app = QtGui.QApplication([])
    # identifiers for QSettings persistent application settings
    app.setOrganizationName('battaglia_lab')
    app.setOrganizationDomain('science.ru.nl')
    app.setApplicationName('FL593FL')

    window = Main(app, *args, **kwargs)
    window.show()
    window.raise_()  # needed on OSX?

    sys.exit(app.exec_())

if __name__ == "__main__":
    # Command line parsing
    import argparse
    parser = argparse.ArgumentParser(prog='PyFL593FL Qt GUI')
    parser.add_argument('-d', '--DEBUG', action='store_true', 
                        help='Debug mode. Actually, only disables exit confirmation.')
    parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=__version__))
    cli_args = parser.parse_args()

    if cli_args.DEBUG:
        NO_EXIT_CONFIRMATION = True 
        LOG_LEVEL = logging.DEBUG

    logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Let's roll
    main()
