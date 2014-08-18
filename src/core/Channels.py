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


class Channel(object):
    def __init__(self, chan_num=0):
        self.log = logging.getLogger(__name__)
        self.device = None
        self.id = chan_num
        self.packets = {}

    def get(self, shorthand):
        """Grab a value identified by shorthand descriptor."""
        assert shorthand in self.packets.keys()
        return self.push(self.packets[shorthand])

    def push(self, packet):
        """Helper transmitting command to device and handling return value."""
        self.log.debug('Pushing packet: {}'.format(str(packet)))
        rp = self.device.transceive(packet)
        error = rp.end_code
        if error is not ERR_OK:
            self.log.error('Channel {} response packet returned error #{}: {}'.format(self.id, error,
                                                                                      ERROR_DICT[error]))
        return error, rp


class StatusChannel(Channel):
    _track = None
    _model = None
    _serial = None
    _fw_version = None
    _dev_type = None
    _channel_count = None
    _identify = None
    _enable = None

    _output_enabled = None
    _remote_enabled = None
    _external_enabled = None

    def __init__(self, chan_num=0, *args, **kwargs):
        super(StatusChannel, self).__init__(*args, **kwargs)
        self.log = logging.getLogger(self.__class__.__name__)
        self.id = chan_num

        self.cmd = [('read_model', TYPE_READ, CMD_MODEL),
                    ('read_serial', TYPE_READ, CMD_SERIAL),
                    ('read_fwver', TYPE_READ, CMD_FWVER),
                    ('read_devtype', TYPE_READ, CMD_DEVTYPE),
                    ('read_num_chan', TYPE_READ, CMD_CHANCT),
                    ('read_alarms', TYPE_READ, CMD_ALARM),
                    ('read_enable', TYPE_READ, CMD_ENABLE)]

        # pre-built packages that don't need extra
        self.log.debug('Building control channel packet dictionary')
        self.packets = {p[0]: CommandPacket(channel=self.id,
                                            op_type=p[1],
                                            op_code=p[2])
                        for p in self.cmd if p[1] in [TYPE_READ, TYPE_MIN, TYPE_MAX]}

        self.alarm_state = {n: False for n in range(NUM_ALARMS)}

    def initialize(self, device):
        """Once device attached, channel can be initiated using data from device."""
        self.log.debug('Initializing status channel')
        self.device = device

        # loop to avoid initial troubles in communication (device boots?)
        for n in range(MAX_CONN_RETRIES):
            time.sleep(TIMEOUT/1000.)  # sleep a moment to let device boot up
            e, rp = self.set_remote_enable(START_REMOTE_ENABLE_STATE)
            self.log.debug(e)
            if rp is not None:
                break
            else:
                self.log.debug("Failed conversation attempt {0:d}".format(n+1))
        else:
            self.log.error("Status channel failed to transceive after {} retries.".format(MAX_CONN_RETRIES))
            raise BaseException("Failed to communicate with device!")
        self.log.debug('Control channel initialized!')

    def update(self):
        """Update attached properties."""
        self.log.debug('Updating control channel')
        self.update_alarms()

    def update_alarms(self):
        """Update alarm flags."""
        self.log.debug('Updating control channel alarms')
        e, rp = self.get('read_alarms')
        if e is not None:
            self.alarm_state = {n: rp.data[n] == FLAG_ON for n in range(NUM_ALARMS)}
        else:
            self.alarm_state = None

    def show_alarms(self):
        # TODO: Optionally specify flags.
        # TODO: Optionally hand packet from which to extract flags.
        self.log.info('Alarm flag states:')
        for key, item in self.alarm_state.items():
            flag = 'ON' if item == FLAG_ON else 'OFF'
            self.log.info('{0:<20s}: {1:s}\n'.format(ALARM_FLAG_DICT[key], flag))

    def get_device_type(self):
        """Device type. Not really used for anything."""
        if self._dev_type is None:
            # update device type
            e, rp = self.get('read_devtype')
            if not e:
                self._dev_type = rp.data_str()
        return self._dev_type

    def get_model(self):
        """Device model."""
        if self._model is None:
            # Update model
            e, rp = self.get('read_model')
            if not e:
                self._model = rp.data_str()
        return self._model

    def get_fw_version(self):
        """Firmware version."""
        if self._fw_version is None:
            e, rp = self.get('read_fwver')
            if not e:
                self._fw_version = '{0:.2f}'.format(float(rp.data_str()))
        return self._fw_version

    def get_serial(self):
        """Device serial number."""
        if self._serial is None:
            e, rp = self.get('read_serial')
            if not e:
                self._serial = rp.data_str()
        return self._serial

    def get_num_channels(self):
        if self._channel_count is None:
            # update number of available channels
            e, rp = self.get('read_num_chan')
            if not e:
                self._channel_count = int(rp.data_str())
        return self._channel_count if self._channel_count is not None else 0

    def get_output_enable(self):
        """Output enabled when all three enable conditions are met:
        XEN, LEN, REN must be true.
        """
        return self.alarm_state[0]

    def get_external_enable(self):
        return self.alarm_state[1]

    def get_local_enable(self):
        return self.alarm_state[2]

    def get_remote_enable(self):
        return self.alarm_state[3]

    def set_remote_enable(self, state):
        packet = CommandPacket(op_type=TYPE_WRITE,
                               op_code=CMD_ENABLE,
                               data=[FLAG_ON if state else FLAG_OFF])
        e, rp = self.push(packet)
        print e, rp, 'SUCCESSFUL PUSH!'
        self.log.debug('Remote enable set to: {}'.format(EXIT_REMOTE_ENABLE_STATE))
        return e, rp

    def close(self):
        # When exiting, disable the remote enable flag to reduce risk of accidental pew pew!
        self.set_remote_enable(EXIT_REMOTE_ENABLE_STATE)


class LaserChannel(Channel):
    _mode = None
    _max = None
    _set = None
    _imon = None
    _pmon = None

    def __init__(self, name=None, *args, **kwargs):
        super(LaserChannel, self).__init__(*args, **kwargs)
        self.log = logging.getLogger(self.__class__.__name__)
        self.name = name if name is not None else 'Channel {}'.format(self.id)

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
        self.packets = {p[0]: CommandPacket(channel=self.id,
                                            op_type=p[1],
                                            op_code=p[2])
                        for p in self.cmd if p[1] in [TYPE_READ, TYPE_MIN, TYPE_MAX]}

    def initialize(self, device):
        """First things to do once device is ready to talk to."""
        self.device = device
        self.log.debug('Initializing laser channel {0:d}'.format(self.id))
        self.zero(AUTO_START_ZERO_LIMIT, AUTO_START_ZERO_SET)

    def zero(self, zero_limit, zero_setpoint):
        """Zero the limits and/or setpoints for this channel."""
        if zero_limit:
            self.log.debug('Zeroing limit Channel {0:d}'.format(self.id))
            self.set_limit(0.0)
        if zero_setpoint:
            self.log.debug('Zeroing setpoint Channel {0:d}'.format(self.id))
            self.set_setpoint(0.0)

    def update(self):
        """Update attached properties"""
        # self.log.debug('Updating laser channel {0:d}'.format(self.id))

        # Get current value for (_target, action)
        update_list = [
            ('_mode', bool),
            ('_imon', float),
            ('_pmon', float),
            ('_limit', float),
            ('_set', float)]
        for item in update_list:
            e, rp = self.get('read'+item[0])
            if not e:
                setattr(self, [item[0]], item[1](rp.data_str()))

        # show limit
        rp = self.device.transceive(self.packets['max_limit'])
        if rp is not None:
            print rp.data_str

    def get_mode(self):
        return self._mode

    def get_imon(self):
        return self._imon * 1000.

    def get_pmon(self):
        return self._pmon * 1000.

    def get_max(self):
        return self._max * 1000.

    def set_max(self, value):
        self.set_limit(value)

    def set_limit(self, value):
        packet = CommandPacket(channel=self.id,
                               op_type=TYPE_WRITE,
                               op_code=CMD_LIMIT,
                               data=[ord(c) for c in str(float(value))])
        rp = self.device.transceive(packet)

    def get_setpoint(self):
        return self._set * 1000.

    def set_setpoint(self, value):
        packet = CommandPacket(channel=self.id,
                               op_type=TYPE_WRITE,
                               op_code=CMD_SETPOINT,
                               data=[ord(c) for c in str(float(value))])
        e, rp = self.push(packet)

    def close(self):
        self.zero(AUTO_EXIT_ZERO_LIMIT, AUTO_EXIT_ZERO_SET)