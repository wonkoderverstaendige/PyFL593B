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


class FL593B(object):

    _model = None
    _fwver = None
    _channel_count = None
    _output_enabled = None
    _remote_enabled = None
    _external_enabled = None

    class Channel(object):
        _mode = None
        _max = None
        _set = None

        def __init__(self, parent, chan_type=None, name=None):
            self.name = name if name is not None else 'Unknown'
            self.channel_type = chan_type if chan_type is not None else 'control'

            if self.channel_type == 'control':
                self.stuff = 'control stuff'
            else:
                self.stuff = 'laser channel stuff'

        def update(self):
            """Update attached properties"""
            pass

        @property
        def mode(self):
            if self._mode is None:
                pass
            else:
                return self._mode

        @property
        def imon(self):
            pass

        @property
        def pmon(self):
            pass

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

        self.channels = {0: Channel(chan_type='control', name='Control'),
                         1: Channel(chan_type='laser', name='Channel 1'),
                         2: Channel(chan_type='laser', name='Channel 1')}

        # TODO: That looks like a stupid idea. Maybe separate, then I could iterate over the channels.
        self.control = self.channels[0]
        self.alarms = dict()

    def attach(self, configuration, name=None, vendorId=VENDOR_ID, productID=PRODUCT_ID):
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
        self.log.info('Attached device %s', self.device)

        # Not necessary, as this is not an HID?
        try:
            self.log.info('Attempting to detach kernel driver...')
            self.device.detach_kernel_driver(0)
            self.log.debug('Kernel driver detached.')
        except:  # this usually mean that kernel driver has already been detached
            self.log.debug('Kernel driver detachment failed.')

        self.show_configurations()
        try:
            self.log.debug('Setting device configuration {0:d}'.format(configuration))
            self.device.set_configuration(configuration)
        except usb.core.USBError as error:
            raise error

    def transceive(self, cmd_packet):
        """This method was proudly named by Tim Schroeder, as is generously provided for by cookies of the same.

        For more information on the adopt-a-method program, please contact the author.
        """
        # Write command packet
        try:
            #self.show_packet(cmd_packet)
            bw = self.endpoint_out.write(cmd_packet.packet)
            self.log.debug('{0:d} bytes written'.format(bw))
        except usb.USBError as error:
            raise error

        # Read back result
        try:
            resp_packet = ResponsePacket(self.endpoint_in.read(self.endpoint_in.wMaxPacketSize, 100))
            self.log.debug('{0:d} bytes received'.format(len(resp_packet)))
            #self.show_packet(resp_packet)
        except usb.USBError as error:
            raise error
        return resp_packet

    def show_configurations(self):
        """Print/log all available configurations

        Pretty useless, always returns 1. :D
        """
        for c, cfg in enumerate(self.device):
            self.log.info('Configuration %d: %s' % (c, str(cfg.bConfigurationValue) + '\n'))

    def show_interfaces(self):
        """Print/log all available interfaces

        Not sure this is actually a thing...
        """
        for i, interface in enumerate(self.config):
            self.log.info('Configuration %d: %s' % (i, str(interface) + '\n'))

    def show_endpoints(self):
        """Print/log all available endpoints

        Not sure this is actually a thing...
        """
        for i, interface in enumerate(self.config):
            self.log.info('Configuration %d: %s' % (i, str(interface) + '\n'))

    def show_packet(self, packet):
        """Logs response onto standard output, or logger
        """
        self.log.debug(packet)

    def show_alarms(self, packet=None):
        """Output current state of alarm flag(s)."""
        # TODO: Optionally specify flags.
        # TODO: Optionally hand packet from which to extract flags.

        self.log.info('Alarm flag states:')
        for i in range(10):
            flag = 'ON' if packet[i] == FLAG_ON else 'OFF'
            self.log.info('{0:<20s}: {1:s}\n'.format(ALARM_FLAG_DICT[i], flag))

    def update_alarms(self):
        if self.log is not None:
            self.log.debug('Updating alarm states')
        pass

    # def static_property_decorator(self, device, op_code, dev_type=0x00, channel=0, op_type=TYPE_READ, data=None):
    #     """Decorator for device properties."""
    #     def wrap(prop):
    #         print "Inside wrap()"
    #         assert device is not None
    #         data = None
    #
    #         def transceive(cmd_packet):
    #             cmd_packet = CommandPacket(dev_type, channel, op_type, op_code, data)
    #             rsp_data = device.transceive(cmd_packet)
    #
    #         def wrapped_f(*args):
    #             print "Inside wrapped_f()"
    #             print "Decorator arguments:", arg1, arg2, arg3
    #             prop(*args)
    #             print "After f(*args)"
    #         return wrapped_f
    #
    #     return wrap

    @property
    def is_ready(self):
        return False

    @property
    def output_enable(self):
        """Output enabled when all three enable conditions are met:
        XEN, LEN, REN must be true.
        """
        pass
        #return self.alarms[ALARM_FLAG_DICT[0]]

    @property
    def external_enable(self):
        return self.alarms[ALARM_FLAG_DICT[1]]

    @property
    def local_enable(self):
        return self.alarms[ALARM_FLAG_DICT[2]]

    @property
    def remote_enable(self):
        if self.alarms is None:
            self.update_alarms()
        self.log.debug('Output enabled:')
        return self.alarms[ALARM_FLAG_DICT[3]]

    @remote_enable.setter
    def remote_enable(self, state):
        rsp_packet = self.transceive(CommandPacket(op_type=TYPE_WRITE, op_code=CMD_ENABLE,
                                                   data=[FLAG_ON if state else FLAG_OFF]))
        print repr(rsp_packet)

    @property
    def parallel(self):
        pass

    @property
    def identify(self):
        pass

    @property
    def write(self):
        pass

    @property
    def calibrate(self):
        pass

    @property
    def model(self):
        self.log.debug('Model description:')
        rsp_packet = self.transceive(CommandPacket(op_type=TYPE_READ, op_code=CMD_MODEL))
        return rsp_packet.data.tostring().strip(chr(0))

    @property
    def fwver(self):
        self.log.debug('Firmware version:')
        rsp_packet = self.transceive(CommandPacket(op_type=TYPE_READ, op_code=CMD_FWVER))
        return rsp_packet.data.tostring().strip(chr(0))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    dev = FL593B()
    print repr(dev.model)
    print repr(dev.fwver)
    dev.remote_enable = False
    # run REPL here

    import cmd

    # DO MAGIC!