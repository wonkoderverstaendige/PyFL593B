# -*- coding: utf-8 -*-
"""
Created on 14 Aug 2014 2:37 PM
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

"""

import logging
from PyQt4 import QtGui, QtCore
from ui import StatusWidgetUi, icons_rc


class StatusWidget(QtGui.QWidget, StatusWidgetUi.Ui_Status):
    """Representation of device status."""
    def __init__(self, parent):
        self.log = logging.getLogger(__name__)
        super(StatusWidget, self).__init__()
        self.setupUi(self)
        self.parent = parent
        self.device = None

        # Control widget
        self.push_REN.toggled.connect(self.toggle_remote_enable)

    def initialize(self):
        self.device = self.parent.device
        assert self.device is not None
        if self.device.model is not None:
            self.lbl_dev_name.setText(self.device.model)
        if self.device.fwver is not None:
            self.lbl_fw_ver.setText(self.device.fwver)
        if self.device.serial is not None:
            self.lbl_serial_num.setText(self.device.serial)

    def refresh(self):
        if self.device is None:
            return
        self.refresh_enable_flags()

    def set_fps(self, elapsed):
        self.lbl_fps.setText('{0:.0f} Hz'.format(1000./elapsed))

    def refresh_enable_flags(self):
        """Update enable flag indicators for local, external and remote flags."""

        self.toggle_laser_warning(self.device.control.output_enable)

        self.set_enable_icon(self.lbl_external_icon, self.device.control.external_enable)
        self.set_enable_icon(self.lbl_output_icon, self.device.control.output_enable)
        self.set_enable_icon(self.lbl_local_icon, self.device.control.local_enable)
        self.push_REN.setChecked(self.device.control.remote_enable)

    def toggle_remote_enable(self, state):
        """Toggle the state of the remote enable flag when toggling the checkbutton."""
        if self.device is None:
            return
        self.log.info('Setting remote enable {0:s}'.format('ON' if state else 'OFF'))
        self.device.control.remote_enable = state

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
