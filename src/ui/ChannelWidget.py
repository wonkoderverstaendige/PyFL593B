#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 4/8/14 2:14 PM 2013
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

"""

import logging
from PyQt4 import QtGui, QtCore
from ui import ChannelUi


class ChannelWidget(QtGui.QWidget, ChannelUi.Ui_Channel):
    def __init__(self, parent, num_channel):
        self.log = logging.getLogger(__name__)
        super(ChannelWidget, self).__init__()
        self.setupUi(self)
        self.parent = parent
        self.groupBox.setTitle('Channel {0:d}'.format(num_channel))
        self.num_channel = num_channel
        self.laser_channel = None

        self.slider_iset.valueChanged[int].connect(self.set_setpoint)
        self.spin_set.valueChanged[int].connect(self.set_setpoint)

        self.slider_imax.valueChanged[int].connect(self.set_limit)
        self.spin_max.valueChanged[int].connect(self.set_limit)

    def initialize(self, channel):
        self.laser_channel = channel

    def refresh(self):
        if self.laser_channel is not None:
            assert self.laser_channel.mode is not None
            if self.laser_channel.mode:
                self.radio_CC.setChecked(True)
            else:
                self.radio_CP.setChecked(True)

            # Current and power levels
            imon = self.laser_channel.imon
            pmon = self.laser_channel.pmon
            limit = self.laser_channel.max
            setpoint = self.laser_channel.setpoint

            # Current and power levels
            self.progbar_imon.setValue(imon if int(imon) >= 0 else 0)
            self.lbl_imon_dbg.setText('{0:0=5.1f}mA'.format(imon))
            self.progbar_pmon.setValue(pmon if int(pmon) >= 0 else 0)
            self.lbl_pmon_dbg.setText('{0:0=5.1f}mA'.format(pmon))

            # Limit
            self.lbl_limit_dbg.setText('{0:0=5.1f}mA'.format(limit))
            self.slider_imax.setValue(int(limit))
            if self.spin_max.value() != int(limit):
                self.spin_max.setValue(int(limit))

            # Setpoint
            ## Limit is maximum for setpoint
            self.spin_set.setMaximum(int(limit))
            self.slider_iset.setMaximum(int(limit))
            if self.spin_set.value() != int(setpoint):
                self.spin_set.setValue(int(setpoint))
            self.slider_iset.setValue(int(setpoint))
            self.lbl_set_dbg.setText('{0:0=5.1f}mA'.format(setpoint))

    def set_setpoint(self, value):
        if self.laser_channel is not None:
            self.log.debug('updating setpoint of channel {0:d}'.format(self.laser_channel.id))
            self.laser_channel.set_setpoint(value/1000.)

    def set_limit(self, value):
        if self.laser_channel is not None:
            self.log.debug('Setting current limit of channel {0:d}'.format(self.laser_channel.id))
            self.laser_channel.set_limit(value/1000.)


