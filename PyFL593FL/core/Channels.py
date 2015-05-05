#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 05 Apr 2014 3:27 AM
@author: <'Ronny Eichler'> ronny.eichler@gmail.com
"""

import time
import logging
from constants import *
from util import memoize_with_expiry, unpack_string


class Channel(object):
    def __init__(self, chan_num=0):
        self.log = logging.getLogger(__name__)
        self.device = None
        self.id = CHANNEL_DICT_REV[chan_num]

    @memoize_with_expiry()
    def read(self, op_code):
        """Read a value from field"""
        command = " ".join([self.id, OP_TYPE_DICT_REV[TYPE_READ], OP_CODE_DICT_REV[op_code]])
        response = unpack_string(self.device.transceive(command))
        if response.end_code != ERR_OK:
            raise ValueError("Reading failed with Error #{}".format(response.end_code))
        return response

    def write(self, op_code, data):
        """Write data to a field, handle response/error code"""
        command = " ".join([self.id, OP_TYPE_DICT_REV[TYPE_WRITE], OP_CODE_DICT_REV[op_code], str(data)])
        response = unpack_string(self.device.transceive(command))
        if response.end_code != ERR_OK:
            raise ValueError("Writing failed with Error #{}".format(response.end_code))
        return response

    @memoize_with_expiry()
    def min(self, op_code):
        """Read max value of property"""
        command = " ".join([self.id, OP_TYPE_DICT_REV[TYPE_MIN], OP_CODE_DICT_REV[op_code]])
        response = unpack_string(self.device.transceive(command))
        if response.end_code != ERR_OK:
            raise ValueError("Min failed with Error #{}".format(response.end_code))
        return response

    @memoize_with_expiry()
    def max(self, op_code):
        """Read min value of property"""
        command = " ".join([self.id, OP_TYPE_DICT_REV[TYPE_MAX], OP_CODE_DICT_REV[op_code]])
        response = unpack_string(self.device.transceive(command))
        if response.end_code != ERR_OK:
            raise ValueError("Max failed with Error #{}".format(response.end_code))
        return response


class StatusChannel(Channel):
    def __init__(self, *args, **kwargs):
        super(StatusChannel, self).__init__(*args, **kwargs)
        self.log = logging.getLogger(self.__class__.__name__)

        self.alarm_states = {n: False for n in range(NUM_ALARMS)}

    def initialize(self, device):
        """Once device attached, channel can be initiated using data from device."""
        self.log.debug('Initializing status channel')
        assert device is not None
        self.device = device

        # loop to avoid initial troubles in communication (device boots?)
        for n in range(MAX_CONN_RETRIES):
            time.sleep(TIMEOUT/1000.)  # sleep a moment to let device boot up
            try:
                self.set_remote_enable(START_REMOTE_ENABLE_STATE)
                break
            except ValueError as error:
                self.log.debug("Failed conversation attempt {} w/ error: {}".format(n+1, error))
        else:
            self.log.error("Status channel failed to transceive after {} retries.".format(MAX_CONN_RETRIES))
            raise BaseException("Failed to communicate with device!")
        self.log.debug('Control channel initialized!')

    def update(self):
        """Update attached properties."""
        self.log.debug('Updating control channel')
        self.update_alarms()

    def update_alarms(self):
        """Update all alarm flags."""
        # FIXME: Failure to read alarms should set states to None which can be used by
        # the UI to indicate uncertainty of the alarm states, preventing false negative indication
        self.log.debug('Updating control channel alarms')
        response = self.read(CMD_ALARM)
        alarms = map(ord, list(response.data))
        self.log.debug("Alarm update response: {}".format(alarms))
        self.alarm_states = {n: alarms[n] == FLAG_ON for n in range(NUM_ALARMS)}

    def show_alarms(self):
        """Helper method to conveniently print current alarm flag states in human
        readable format."""
        # TODO: Optionally specify flags.
        self.log.log(LOG_LVL_VERBOSE, 'Current alarm flag states:')
        for key, state in self.alarm_states.items():
            self.log.info('{0:<7s}: {1:s}'.format(ALARM_FLAG_DICT_REV[key], 'ON' if state else 'OFF'))

    def get_device_type(self):
        """Device type. Not really used for anything."""
        response = self.read(CMD_DEVTYPE)
        return response.data

    def get_model(self):
        """Device model."""
        response = self.read(CMD_MODEL)
        return response.data

    def get_fw_version(self):
        """Firmware version."""
        response = self.read(CMD_FWVER)
        return response.data

    def get_serial(self):
        """Device serial number."""
        response = self.read(CMD_SERIAL)
        return response.data

    def get_num_channels(self):
        """Number of channels currently supported by the device. Switching modes may affect that."""
        response = self.read(CMD_CHANCT)
        return int(response.data)

    def get_output_enable(self):
        """Output enabled when all three enable conditions are met:
        XEN, LEN, REN must be true.
        """
        return self.alarm_states[ALARM_OUT]

    def get_external_enable(self):
        """NT pin on connector J102, currently connected to toggle switch at power supply.
        Pulled HIGH when enabled."""
        return self.alarm_states[ALARM_XEN]

    def get_local_enable(self):
        """Toggle switch on FL593FL PCB."""
        return self.alarm_states[ALARM_LEN]

    def get_remote_enable(self):
        """Software enable. Seems to require active USB connection?"""
        return self.alarm_states[ALARM_REN]

    def set_remote_enable(self, state):
        self.write(CMD_ENABLE, data=chr(FLAG_ON if state else FLAG_OFF))
        self.log.debug('Remote enable set to: {}'.format(state))

    def close(self):
        # When exiting, disable the remote enable flag to reduce risk of accidental pew pew!
        self.set_remote_enable(EXIT_REMOTE_ENABLE_STATE)


class LaserChannel(Channel):
    def __init__(self, *args, **kwargs):
        super(LaserChannel, self).__init__(*args, **kwargs)
        self.log = logging.getLogger(self.__class__.__name__+'[{}]'.format(self.id))

    def initialize(self, device):
        """First things to do once device is ready to talk to."""
        self.log.debug('Initializing with device {}'.format(device))
        assert device is not None
        self.device = device
        self.zero(zero_limit=AUTO_START_ZERO_LIMIT,
                  zero_setpoint=AUTO_START_ZERO_SET)

    def zero(self, zero_limit=True, zero_setpoint=True):
        """Zero the limits and/or setpoint for this channel.
        Useful on startup, just because, and on shutdown."""
        # TODO: Zero-ing buttons in the GUI to quickly reset everything
        if zero_limit:
            self.log.debug('Zeroing limit')
            self.set_limit(0.0)
        if zero_setpoint:
            self.log.debug('Zeroing setpoint')
            self.set_setpoint(0.0)

    def update(self):
        """Call getter methods for channel parameters. With memoization will keep the
        values updated for sequential reading by a remote interface without slow-down caused
        by transmission delays."""
        self.log.debug('Updating laser channel '.format(self.id))
        # Get current value for (_target, action)
        update_list = [self.get_mode, self.get_imon, self.get_pmon,
                       self.get_limit, self.get_setpoint]
        for fn in update_list:
            fn()

    def get_mode(self):
        """Get feedback mode (power or current)"""
        response = self.read(CMD_MODE)
        return response.data

    def set_mode(self, mode):
        """Set setpoint (current or power, as per tracking mode) in [mA]"""
        raise NotImplementedError
        # response = self.write(CMD_MODE, mode)
        # return response.data.strip('\x00')

    def get_track(self):
        raise NotImplementedError
        # response = self.read(CMD_TRACK)
        # return response.data.strip('\x00')

    def get_imon(self):
        """Get current monitor in [mA]"""
        response = self.read(CMD_IMON)
        return float(response.data) * 1000.

    def get_pmon(self):
        """Get power monitor in [mA]"""
        response = self.read(CMD_PMON)
        return float(response.data) * 1000.

    def get_limit(self):
        """CGet limit (current or power, as per tracking mode) in [mA]"""
        response = self.read(CMD_LIMIT)
        return float(response.data) * 1000.

    def set_limit(self, value):
        """Set limit (current or power, as per tracking mode) in [mA]"""
        response = self.write(CMD_LIMIT, str(float(value)))
        return float(response.data) * 1000.

    def get_setpoint(self):
        """CGet set setpoint (current or power, as per tracking mode) in [mA]"""
        response = self.read(CMD_SETPOINT)
        return float(response.data) * 1000.

    def set_setpoint(self, value):
        """Set setpoint (current or power, as per tracking mode) in [mA]"""
        response = self.write(CMD_SETPOINT, str(float(value)))
        return float(response.data) * 1000.

    def close(self):
        """Set limit and setpoint to zero if configured to do so. Should prevent startup with
        unsafe values, even if REN is reset."""
        self.zero(zero_limit=AUTO_EXIT_ZERO_LIMIT,
                  zero_setpoint=AUTO_EXIT_ZERO_SET)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    from Devices import USB
    with USB() as dev:
        sc = StatusChannel()
        sc.initialize(dev)
        sc.update()
        sc.show_alarms()
        lds = [LaserChannel(chan_num=channel) for channel in [1, 2]]
        for ld in lds:
            ld.initialize(dev)
            ld.update()
            time.sleep(0.1)
            print '{}: {} mA'.format(ld.id, ld.get_imon())
            print '{}: {} mA'.format(ld.id, ld.get_pmon())
            print '{}: {} mA'.format(ld.id, ld.get_imon())  # should be cached
            print '{}: {} mA'.format(ld.id, ld.get_pmon())
            time.sleep(0.2)
            print '{}: {} mA'.format(ld.id, ld.get_imon())  # should be refreshed
            print '{}: {} mA'.format(ld.id, ld.get_pmon())
            time.sleep(0.1)
