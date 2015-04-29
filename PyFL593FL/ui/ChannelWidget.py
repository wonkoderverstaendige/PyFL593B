#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 14 Aug 2014 2:20 PM
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

"""

import logging
from PyQt4 import QtGui, QtCore
import ChannelWidgetUi


class ChannelWidget(QtGui.QWidget, ChannelWidgetUi.Ui_Channel):
    """GUI representation of a single controlled channel. Provides UI elements to
    display (and control, where applicable) values, limits and setpoints for
    applied current/light power.
    """
    def __init__(self, parent, channel_id):
        self.log = logging.getLogger(__name__)
        super(ChannelWidget, self).__init__()
        self.setupUi(self)
        self.parent = parent
        self.groupBox.setTitle('Unknown channel')
        self.num_channel = channel_id
        self.controlled_channel = None

        # controls for setpoint
        self.slider_iset.valueChanged[int].connect(self.set_setpoint)
        self.spin_set.valueChanged[int].connect(self.set_setpoint)

        # controls for limit
        self.slider_imax.valueChanged[int].connect(self.set_limit)
        self.spin_max.valueChanged[int].connect(self.set_limit)

    def initialize(self, channel):
        assert channel is not None
        self.groupBox.setTitle(channel.id)
        self.controlled_channel = channel

    def refresh(self):
        if self.controlled_channel is not None:
            assert self.controlled_channel.get_mode() is not None
            if self.controlled_channel.get_mode():
                self.radio_CC.setChecked(True)
            else:
                self.radio_CP.setChecked(True)

            # Raw current and power and setpoint values
            imon = self.controlled_channel.get_imon()
            pmon = self.controlled_channel.get_pmon()
            limit = self.controlled_channel.get_limit()
            setpoint = self.controlled_channel.get_setpoint()

            # Current and power levels
            self.progbar_imon.setValue(imon if int(imon) >= 0 else 0)
            self.lbl_imon_dbg.setText('{0:0=5.1f}mA'.format(imon))
            self.progbar_pmon.setValue(pmon if int(pmon) >= 0 else 0)
            self.lbl_pmon_dbg.setText('{0:0=5.1f}mA'.format(pmon))

            # Limit (current for CC, power for CP mode)
            self.lbl_limit_dbg.setText('{0:0=5.1f}mA'.format(limit))
            self.slider_imax.setValue(int(limit))
            if self.spin_max.value() != int(limit):
                self.spin_max.setValue(int(limit))

            # Setpoint (current for CC, power for CP mode)
            self.spin_set.setMaximum(int(limit))
            self.slider_iset.setMaximum(int(limit))
            if self.spin_set.value() != int(setpoint):
                self.spin_set.setValue(int(setpoint))
            self.slider_iset.setValue(int(setpoint))
            self.lbl_set_dbg.setText('{0:0=5.1f}mA'.format(setpoint))

    def set_setpoint(self, value):
        """Changes the value of the setpoint for the controlled channel.
        Unit depends on CC or CP mode.
        """
        if self.controlled_channel is not None:
            self.log.debug('Updating setpoint for {}'.format(self.controlled_channel.id))
            self.controlled_channel.set_setpoint(value/1000.)

    def set_limit(self, value):
        """Changes the value of the limit for the controlled channel.
        Unit depends on CP or CC mode.
        """
        if self.controlled_channel is not None:
            self.log.debug('Setting current limit for {}'.format(self.controlled_channel.id))
            self.controlled_channel.set_limit(value/1000.)
