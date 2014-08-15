#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 05 Apr 2014 3:27 AM
@author: <'Ronny Eichler'> ronny.eichler@gmail.com
"""

import time
import logging
from fl593fl_constants import *
from Packets import CommandPacket, ResponsePacket


class LaserChannel(object):
    _mode = None
    _max = None
    _set = None
    _imon = None
    _pmon = None

    def __init__(self, name=None, channel_number=0):
        self.log = logging.getLogger(__name__)
        self.id = channel_number
        self.name = name if name is not None else 'Channel {}'.format(self.id)
        self.device = None

        # channel type register value
        # "0 read setpoint -"
        # "0 read

        self.cmd = [('read_imon', TYPE_READ, CMD_IMON),
                    ('read_pmon', TYPE_READ, CMD_PMON),
                    #
                    ('read_limit', TYPE_READ, CMD_LIMIT),
                    ('write_limit', TYPE_WRITE, CMD_LIMIT),
                    ('min_limit', TYPE_MIN, CMD_LIMIT),
                    ('max_limit', TYPE_MAX, CMD_LIMIT),
                    #
                    ('read_set', TYPE_READ, CMD_SETPOINT),
                    ('write_set', TYPE_WRITE, CMD_SETPOINT),
                    ('min_set', TYPE_MIN, CMD_SETPOINT),
                    ('max_set', TYPE_MAX, CMD_SETPOINT),
                    #
                    ('read_mode', TYPE_READ, CMD_MODE),
                    ('write_mode', TYPE_WRITE, CMD_MODE)]

        # pre-built packages that don't need extra data
        self.log.debug('Building laser channel {0:d} packet dictionary'.format(self.id))
        self.packets = {p[0]: CommandPacket(channel=self.id, op_type=p[1], op_code=p[2])
                        for p in self.cmd if p[1] in [TYPE_READ, TYPE_MIN, TYPE_MAX]}

    def initialize(self, device):
        """First things to do once device is ready to talk to."""
        self.device = device
        self.log.debug('Initializing laser channel {0:d}'.format(self.id))
        self.zero(AUTO_START_ZERO_LIMIT, AUTO_START_ZERO_SET)

    def zero(self, zero_limit, zero_setpoint):
        if zero_limit:
            self.log.debug('Zeroing limit Channel {0:d}'.format(self.id))
            self.set_limit(0.0)
        if zero_setpoint:
            self.log.debug('Zeroing setpoint Channel {0:d}'.format(self.id))
            self.set_setpoint(0.0)

    def update(self):
        """Update attached properties"""
        self.log.debug('Updating laser channel {0:d}'.format(self.id))
        # update mode
        rp = self.device.transceive(self.packets['read_mode'])
        if rp is not None:
            self._mode = bool(rp.data_str)

        # update imon
        rp = self.device.transceive(self.packets['read_imon'])
        if rp is not None:
            self._imon = float(rp.data_str)

        # update pmon
        rp = self.device.transceive(self.packets['read_pmon'])
        if rp is not None:
            self._pmon = float(rp.data_str)

        # update limit
        rp = self.device.transceive(self.packets['read_limit'])
        if rp is not None:
            self._max = float(rp.data_str)

        # update setpoint
        rp = self.device.transceive(self.packets['read_set'])
        if rp is not None:
            self._set = float(rp.data_str)

        # show limit
        rp = self.device.transceive(self.packets['max_limit'])
        if rp is not None:
            print rp.data_str

    @property
    def mode(self):
        return self._mode

    @property
    def imon(self):
        return self._imon * 1000.

    @property
    def pmon(self):
        return self._pmon * 1000.

    @property
    def max(self):
        return self._max * 1000.

    @max.setter
    def max(self, value):
        self.set_limit(value)

    def set_limit(self, value):
        packet = CommandPacket(channel=self.id,
                               op_type=TYPE_WRITE,
                               op_code=CMD_LIMIT,
                               data=[ord(c) for c in str(float(value))])
        rp = self.device.transceive(packet)

    @property
    def setpoint(self):
        return self._set * 1000.

    @setpoint.setter
    def setpoint(self, value):
        # FIXME: Doesn't work! Always tries to retrieve value and then call it?! WTF!
        self.set_setpoint(value)

    def set_setpoint(self, value):
        # FIXME: For some reason I can't use the setpoint.setter decorator!
        packet = CommandPacket(channel=self.id,
                               op_type=TYPE_WRITE,
                               op_code=CMD_SETPOINT,
                               data=[ord(c) for c in str(float(value))])
        rp = self.device.transceive(packet)

    def close(self):
        self.zero(AUTO_EXIT_ZERO_LIMIT, AUTO_EXIT_ZERO_SET)


class StatusChannel(object):
    _track = None
    _model = None
    _serial = None
    _fwver = None
    _devtype = None
    _channel_count = None
    _identify = None
    _enable = None

    _output_enabled = None
    _remote_enabled = None
    _external_enabled = None

    def __init__(self, chan_num=0):
        self.log = logging.getLogger(__name__)
        self.device = None
        self.id = chan_num

        self.cmd = [('read_model', TYPE_READ, CMD_MODEL),
                    ('read_serial', TYPE_READ, CMD_SERIAL),
                    ('read_fwver', TYPE_READ, CMD_FWVER),
                    ('read_devtype', TYPE_READ, CMD_DEVTYPE),
                    ('read_chanct', TYPE_READ, CMD_CHANCT),
                    ('read_alarm', TYPE_READ, CMD_ALARM),
                    ('read_enable', TYPE_READ, CMD_ENABLE)]

        # pre-built packages that don't need extra
        self.log.debug('Building control channel packet dictionary')
        self.packets = {p[0]: CommandPacket(channel=self.id, op_type=p[1], op_code=p[2])
                        for p in self.cmd if p[1] in [TYPE_READ, TYPE_MIN, TYPE_MAX]}

        self.alarms = {n: False for n in range(10)}

    def initialize(self, device):
        self.log.debug('Initializing status channel')

        self.device = device

        # update model and loop to avoid initial troubles in communication (device boots?)
        # FIXME: Pause for 200-300 ms or so before starting communication
        for n in range(10):
            rp = self.device.transceive(self.packets['read_model'])
            if not rp:
                self.log.error("Failed conversation attempt {0:d}".format(n))
            else:
                self._model = rp.data_str

        if AUTO_START_DISABLE_REMOTE:
            self.log.debug('Disabling remote enable on startup')
            self.remote_enable = False

        # update firmware version
        rp = self.device.transceive(self.packets['read_fwver'])
        if rp is not None:
            self._fwver = '{0:.2f}'.format(float(rp.data_str))

        # update serial number
        rp = self.device.transceive(self.packets['read_serial'])
        if rp is not None:
            self._serial = rp.data_str

        # update device type
        rp = self.device.transceive(self.packets['read_devtype'])
        if rp is not None:
            self._devtype = rp.data_str

        # update number of available channels
        rp = self.device.transceive(self.packets['read_chanct'])
        if rp is not None:
            self._channel_count = int(rp.data_str)
        self.log.debug('Control channel initialized!')

    def update(self):
        """Update attached properties."""
        self.log.debug('Updating control channel')
        self.update_alarms()

    def update_alarms(self):
        """Update alarm flags."""
        self.log.debug('Updating control channel alarms')
        rp = self.device.transceive(self.packets['read_alarm'])
        if rp is not None:
            self.alarms = {n: rp.data[n] == FLAG_ON for n in range(10)}

    def show_alarms(self):
        # TODO: Optionally specify flags.
        # TODO: Optionally hand packet from which to extract flags.
        self.log.info('Alarm flag states:')
        for key, item in self.alarms.items():
            flag = 'ON' if item == FLAG_ON else 'OFF'
            self.log.info('{0:<20s}: {1:s}\n'.format(ALARM_FLAG_DICT[key], flag))

    @property
    def num_channels(self):
        return self._channel_count if self._channel_count is not None else 0

    @property
    def model(self):
        return self._model

    @property
    def fwver(self):
        return self._fwver

    @property
    def serial(self):
        return self._serial

    @property
    def output_enable(self):
        """Output enabled when all three enable conditions are met:
        XEN, LEN, REN must be true.
        """
        return self.alarms[0]

    @property
    def external_enable(self):
        return self.alarms[1]

    @property
    def local_enable(self):
        return self.alarms[2]

    @property
    def remote_enable(self):
        return self.alarms[3]

    @remote_enable.setter
    def remote_enable(self, state):
        self.device.transceive(CommandPacket(op_type=TYPE_WRITE, op_code=CMD_ENABLE,
                                             data=[FLAG_ON if state else FLAG_OFF]))

    def close(self):
        # When exiting, disable the remote enable flag to reduce risk of accidental pew pew!
        if AUTO_EXIT_DISABLE_REMOTE:
            self.log.debug('Disabling remote enable on exit')
            self.remote_enable = False
