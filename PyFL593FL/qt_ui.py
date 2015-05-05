#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 08 Apr 2014 2:14 PM
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

"""

import sys
if sys.hexversion > 0x03000000:
    raise EnvironmentError('Python 3 not supported.')
import argparse
import logging
from PyQt4 import QtGui, QtCore
from ui import MainWindowUi
from ui.StatusWidget import StatusWidget
from ui.ChannelWidget import ChannelWidget
from core.fl593fl import FL593FL
from core.constants import LOG_LVL_VERBOSE
from core import Devices

__version__ = '0.2'
LOG_LEVEL = logging.INFO
NO_EXIT_CONFIRMATION = False


class Main(QtGui.QMainWindow, object):

    def __init__(self, app, *args, **kwargs):
        QtGui.QMainWindow.__init__(self)
        self.log = logging.getLogger(__name__)
        self.fl593fl = None
        self.app = app
        self.log.debug("Readying MainUi Window")
        self.ui = MainWindowUi.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.actionReset.triggered.connect(self.reset_device)
        self.ui.actionQuit.triggered.connect(self.close)

        # Channel widgets
        self.channel_widgets = []

        # Status widget shows and interacts with flags and warning label
        self.status_widget = StatusWidget(self)
        self.ui.frame_layout.addWidget(self.status_widget)

        # Main loop control stuff
        self.stopwatch = QtCore.QElapsedTimer()
        self.stopwatch.start()
        self.running = True  # to prevent GUI refresh during device shutdown
        self.gui_refresh_interval = 0
        self.elapsed = self.gui_refresh_interval if self.gui_refresh_interval > 0 else 30
        QtCore.QTimer.singleShot(0, self.initialize)  # fires when event loop starts

    def initialize(self, *args, **kwargs):
        """Set up device and representations once UI was initiated."""
        self.log.debug("Initializing core fl593fl device interface...")

        self.fl593fl = FL593FL(*args, **kwargs)
        assert self.fl593fl is not None

        # add channels/initialize widgets now that we have a working connection
        self.status_widget.initialize(self.fl593fl)
        self.channel_widgets = [ChannelWidget(self, n+1) for n in range(self.fl593fl.status.get_num_channels())]
        for widget in self.channel_widgets:
            self.ui.layout_channels.addWidget(widget)
            widget.initialize(self.fl593fl.channels[widget.num_channel])

        # start main refresh loop
        self.refresh()

    def refresh(self):
        """Main loop processing/updating."""
        if not self.running or self.fl593fl is None:
            return

        # update rate display (smoothed)
        self.elapsed = 0.8*self.elapsed + 0.2*self.stopwatch.restart()
        self.status_widget.set_fps(self.elapsed)

        # have the device update itself fully
        self.fl593fl.update()

        # Refresh widgets
        self.status_widget.refresh()
        for widget in self.channel_widgets:
            widget.refresh()

        # start timer for next refresh
        QtCore.QTimer.singleShot(self.gui_refresh_interval, self.refresh)

    def reset_device(self):
        """Reset device (bus). """
        self.fl593fl.reset()

    def closeEvent(self, event):
        """This party sucks. The moment I find my pants I'm out of here!"""
        if NO_EXIT_CONFIRMATION:
            reply = QtGui.QMessageBox.Yes
        else:
            reply = QtGui.QMessageBox.question(self, 'Exiting...', 'Are you sure?',
                                               QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.running = False
            if self.fl593fl is not None:
                self.fl593fl.close()
            event.accept()
        else:
            event.ignore()


#############################################################
def main(*args, **kwargs):

     # Let's roll
    app = QtGui.QApplication([])

    # identifiers for QSettings persistent application settings
    app.setOrganizationName('battaglia_lab')
    app.setOrganizationDomain('science.ru.nl')
    app.setApplicationName('FL593FL')

    window = Main(app=app, *args, **kwargs)
    window.show()
    window.raise_()  # needed on OSX?

    sys.exit(app.exec_())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='PyFL593FL Qt GUI')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Debug mode. Verbose printing, no exit confirmation.')
    parser.add_argument('--dummy', action='store_true', help='Initiate with dummy device interface sending \
                        random values. Useful for GUI debugging or when user forgot device in the workshop.')
    parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=__version__))
    cli_args = parser.parse_args()

    if cli_args.debug:
        NO_EXIT_CONFIRMATION = True

    logging.addLevelName(LOG_LVL_VERBOSE, "VERBOSE")
    logging.basicConfig(level=LOG_LVL_VERBOSE if cli_args.debug else LOG_LEVEL,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log = logging.getLogger(__name__)

    main(device_interface='dummy' if cli_args.dummy else 'usb')

