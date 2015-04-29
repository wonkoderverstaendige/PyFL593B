# -*- coding: utf-8 -*-
"""
Created on 14 Aug 2014 2:37 PM
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

"""

import logging
from PyQt4 import QtGui, QtCore
import StatusWidgetUi, icons_rc


class StatusWidget(QtGui.QWidget, StatusWidgetUi.Ui_Status):
    """Representation of device status."""
    def __init__(self, parent):
        self.log = logging.getLogger(__name__)
        super(StatusWidget, self).__init__()
        self.setupUi(self)
        self.parent = parent
        self.device = None
        self.status_channel = None

        # Control widget
        self.push_REN.toggled.connect(self.toggle_remote_enable)

    def initialize(self, device):
        assert device is not None
        self.device = None
        self.status_channel = device.status
        if self.status_channel.get_model() is not None:
            self.lbl_dev_name.setText(self.status_channel.get_model())
        if self.status_channel.get_fw_version() is not None:
            self.lbl_fw_ver.setText(self.status_channel.get_fw_version())
        if self.status_channel.get_serial() is not None:
            self.lbl_serial_num.setText(self.status_channel.get_serial())

    def refresh(self):
        if self.status_channel is None:
            return
        self.refresh_enable_flags()

    def set_fps(self, elapsed):
        self.lbl_fps.setText('{0:.0f} Hz'.format(1000./elapsed))

    def refresh_enable_flags(self):
        """Update enable flag indicators for local, external and remote flags."""
        self.toggle_laser_warning(self.status_channel.get_output_enable())

        self.set_enable_icon(self.lbl_external_icon, self.status_channel.get_external_enable())
        self.set_enable_icon(self.lbl_output_icon, self.status_channel.get_output_enable())
        self.set_enable_icon(self.lbl_local_icon, self.status_channel.get_local_enable())
        self.push_REN.setChecked(self.status_channel.get_remote_enable())

    def toggle_remote_enable(self, state):
        """Toggle the state of the remote enable flag when toggling the checkbutton."""
        if self.status_channel is not None:
            self.log.debug('Setting remote enable {0:s}'.format('ON' if state else 'OFF'))
            self.status_channel.set_remote_enable(state)

    def toggle_laser_warning(self, state):
        if self.lbl_laser_warning.isEnabled() != state:
            self.lbl_laser_warning.setEnabled(state)

    @staticmethod
    def set_enable_icon(widget, state):
        """Set pixmap of label with ON or OFF marker from the icons_rc.qrc file.

        Imported from ui.icons_rc."""
        if state:
            widget.setPixmap(QtGui.QPixmap(StatusWidgetUi._fromUtf8(":/icons/enabled_true.png")))
        else:
            widget.setPixmap(QtGui.QPixmap(StatusWidgetUi._fromUtf8(":/icons/enabled_false.png")))
