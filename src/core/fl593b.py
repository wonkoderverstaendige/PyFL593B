#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 4/5/14 3:27 AM 2013
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

FL593B evaluation board USB interface class
"""

import sys

if sys.hexversion > 0x03000000:
    raise EnvironmentError('Python 3 not supported.')

import time
import threading
import array
import logging
import usb.core
import usb.util
from fl593b_constants import *
from Packets import CommandPacket, ResponsePacket


class LaserChannel(object):
    _mode = None
    _max = None
    _set = None
    _imon = None
    _pmon = None

    def __init__(self, parent, name=None, chan_num=0):
        self.log = logging.getLogger(__name__)
        self.name = name if name is not None else 'Unknown'
        self.parent = parent
        self.id = chan_num

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

    def initialize(self):
        """First things to do once device is ready to talk to."""
        self.log.debug('Initializing laser channel {0:d}'.format(self.id))

    def update(self):
        """Update attached properties"""
        self.log.debug('Updating laser channel {0:d}'.format(self.id))
        # update mode
        rp = self.parent.transceive(self.packets['read_mode'])
        if rp is not None:
            self._mode = bool(rp.data_str)
        self.log.debug('Laser channel {0:d} initialized!'.format(self.id))

        # update imon
        rp = self.parent.transceive(self.packets['read_imon'])
        if rp is not None:
            self._imon = float(rp.data_str)

        # update pmon
        rp = self.parent.transceive(self.packets['read_pmon'])
        if rp is not None:
            self._pmon = float(rp.data_str)

        # update pmon
        rp = self.parent.transceive(self.packets['read_limit'])
        if rp is not None:
            self._max = float(rp.data_str)

        # update setpoint
        rp = self.parent.transceive(self.packets['read_set'])
        if rp is not None:
            self._set = float(rp.data_str)

        # show limit
        # rp = self.parent.transceive(self.packets['max_limit'])
        # if rp is not None:
        #     print rp.data_str

    @property
    def mode(self):
        return self._mode

    @property
    def imon(self):
        return self._imon*1000.

    @property
    def pmon(self):
        return self._pmon*1000.

    @property
    def max(self):
        return self._max*1000.

    @max.setter
    def max(self, value):
        self.set_limit(value)

    def set_limit(self, value):
        packet = CommandPacket(channel=self.id,
                               op_type=TYPE_WRITE,
                               op_code=CMD_LIMIT,
                               data=[ord(c) for c in str(float(value))])
        rp = self.parent.transceive(packet)
        if rp:
            self.parent.show_packet(rp)

    @property
    def setpoint(self):
        return self._set*1000.

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
        rp = self.parent.transceive(packet)
        if rp:
            self.parent.show_packet(rp)


class ControlChannel(object):
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

    def __init__(self, parent, chan_num=0):
        self.log = logging.getLogger(__name__)
        self.parent = parent
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

    def initialize(self):
        self.log.debug('Initializing control channel')

        # update model and loop to avoid initial troubles in communication (device boots?)
        for n in range(10):
            rp = self.parent.transceive(self.packets['read_model'])
            if not rp:
                self.log.error("Failed conversation attempt {0:d}".format(n))
            else:
                self._model = rp.data_str

        # update firmware version
        rp = self.parent.transceive(self.packets['read_fwver'])
        if rp is not None:
            self._fwver = rp.data_str

        # update serial number
        rp = self.parent.transceive(self.packets['read_serial'])
        if rp is not None:
            self._serial = rp.data_str

        # update device type
        rp = self.parent.transceive(self.packets['read_devtype'])
        if rp is not None:
            self._devtype = rp.data_str

        # update number of available channels
        rp = self.parent.transceive(self.packets['read_chanct'])
        if rp is not None:
            self._channel_count = int(rp.data_str)
        self.log.debug('Control channel initialized!')

    def update(self):
        """Update attached properties"""
        self.log.debug('Updating control channel')
        self.update_alarms()

    def update_alarms(self):
        """Update alarm flags"""
        #self.log.debug('Updating control channel alarms')
        rp = self.parent.transceive(self.packets['read_alarm'])
        if rp is not None:
            self.alarms = {n: rp.data[n] == FLAG_ON for n in range(10)}
            # for n in range(10):
            #     self.alarms[n] = True if rp.data[n] == FLAG_ON else False  # was 49

    @property
    def channel_count(self):
        return self._channel_count if self._channel_count is not None else 0

    @property
    def model(self):
        return self._model

    @property
    def fwver(self):
        return self._fwver

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
        rp = self.parent.transceive(CommandPacket(op_type=TYPE_WRITE, op_code=CMD_ENABLE,
                                                  data=[FLAG_ON if state else FLAG_OFF]))


class FL593B(object):
    def __init__(self, config=None):
        self.log = logging.getLogger(__name__)
        config = config if config is not None else 1

        # device
        self.device = None
        self.attach(config)
        assert self.device is not None

        # configuration
        self.config = self.device.get_active_configuration()

        # interface
        self.interface = self.config[0, 0]

        # endpoints
        self.endpoint_out, self.endpoint_in = usb.util.find_descriptor(self.interface, find_all=True)
        self.len_receive = self.endpoint_in.wMaxPacketSize
        self.len_transmit = self.endpoint_out.wMaxPacketSize

        self.channels = {}
        self.control = None

        # assuming that everything went according to plan, we can now say hello to the device
        self.initialize()

    def attach(self, configuration, vendorId=VENDOR_ID, productID=PRODUCT_ID):
        """Find and attach to the USB device with given vendorID and productID.
        Overly general, as right now there is only one such combination I know of.
        But why not make it neat?
        """
        try:
            self.log.debug('Trying to attach USB device {0:x}:{1:x}'.format(vendorId, productID))
            self.device = usb.core.find(idVendor=vendorId, idProduct=productID)
        except usb.core.USBError as error:
            raise error
        # TODO: search for a particular name
        if self.device is None:
            raise ValueError('Device not found')
        self.log.info('FL593B attached.')
        self.log.debug('Attached device %s', self.device)

        # Not necessary, as this is not an HID?
        try:
            self.log.debug('Attempting to detach kernel driver...')
            self.device.detach_kernel_driver(0)
            self.log.debug('Kernel driver detached.')
        except:  # this usually mean that kernel driver has already been detached
            self.log.debug('Kernel driver detachment failed. No worries.')

        self.show_configurations()
        try:
            self.log.debug('Setting device configuration {0}'.format(1))
            self.device.set_configuration(configuration)
        except usb.core.USBError as error:
            raise error
        except BaseException as error:
            raise error

        self.log.debug('Device attachment complete.')

    def initialize(self):
        self.log.debug('Initializing device...')
        # The general control and device status channel
        self.control = ControlChannel(self)
        assert self.control is not None
        self.control.initialize()

        # The laser driver channels
        if self.control.channel_count is not None:
            self.channels = {n: LaserChannel(parent=self, chan_num=n) for n in range(1, self.control.channel_count+1)}

        self.log.debug('... done.')

    def update(self):
        self.control.update()
        for n, channel in self.channels.items():
            channel.update()

    def transceive(self, cmd_packet):
        """This method was aptly named by Tim Schroeder, as is generously provided for by cookies of the same.

        For more information on the adopt-a-method program, please contact the author.
        """
        # Write command packet
        try:
            #self.show_packet(cmd_packet)
            bw = self.endpoint_out.write(cmd_packet.packet)
            #self.log.debug('{0:d} bytes written: {1:s}'.format(bw, str(cmd_packet)))
        except usb.USBError as error:
            print "Could not write! %s" % error
            return None

        # Read back result
        try:
            resp_packet = ResponsePacket(self.endpoint_in.read(self.endpoint_in.wMaxPacketSize, TIMEOUT))
            #self.log.debug('{0:d} bytes received: {1:s}'.format(len(resp_packet), str(resp_packet)))
            #self.show_packet(resp_packet)
        except usb.USBError as error:
            print "Could not receive response! %s" % error
            return None

        return resp_packet

    def show_configurations(self):
        """Print/log all available configurations

        Pretty useless, always returns 1. :D
        """
        for c, cfg in enumerate(self.device):
            self.log.debug('Configuration %d: %s' % (c, str(cfg.bConfigurationValue)))

    def show_interfaces(self):
        """Print/log all available interfaces

        Not sure this is actually a thing...
        """
        for i, interface in enumerate(self.config):
            self.log.info('Interface %d: %s' % (i, str(interface) + '\n'))

    def show_endpoints(self):
        """Print/log all available endpoints

        Not sure this is actually a thing...
        """
        # FIXME: Copy'n'paste without change from interfaces... lookup endpoint enumeration!
        for i, interface in enumerate(self.config):
            self.log.info('Interface %d: %s' % (i, str(interface) + '\n'))

    def show_packet(self, packet):
        """Logs response onto standard output, or logger
        """
        self.log.info(repr(packet))

    def show_alarms(self):
        """Output current state of alarm flag(s)."""
        # TODO: Optionally specify flags.
        # TODO: Optionally hand packet from which to extract flags.
        self.log.info('Alarm flag states:')
        for key, item in self.control.alarms.items():
            flag = 'ON' if item == FLAG_ON else 'OFF'
            self.log.info('{0:<20s}: {1:s}\n'.format(ALARM_FLAG_DICT[key], flag))

    @property
    def is_ready(self):
        return False

    @property
    def identify(self):
        pass

    @property
    def model(self):
        self.log.debug('Model description:')
        return self.control.model

    @property
    def fwver(self):
        self.log.debug('Firmware version:')
        return self.control.fwver

    @property
    def channel_count(self):
        return self.control.channel_count

    def reset(self):
        self.device.reset()

    def close(self):
        self.device.reset()
        del self.device


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    dev = FL593B()
    print repr(dev.model)
    print repr(dev.fwver)
    dev.remote_enable = False

    # run REPL here

    # DO MAGIC!