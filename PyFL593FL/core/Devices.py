#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 05 Apr 2014 3:27 AM
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

Different classes representing interfaces to the FL593FL evaluation board.

USB: Direct access via USB through PyUSB
Socket: Connection via ZMQ through e.g. a socket or other ZMQ contexts
Dummy: Virtual device for debugging. Returns semi-random values
"""

import logging
from array import array
from constants import *
from util import encode_command, decode_response
try:
    import usb
except ImportError:
    usb = None

try:
    import zmq
except ImportError:
    zmq = None

from Packets import CommandPacket, ResponsePacket


class Device(object):
    """Generic device interface class."""
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.len_transmit = None
        self.len_receive = None
        self.device = None
        self.num_channels = MAX_NUM_CHAN

    def __enter__(self):
        pass

    def open(self, *args, **kwargs):
        """Open connection to device."""
        self.device = None

    def transceive(self, packet):
        """This method was aptly named by Tim Schroeder, and is generously provided for with cookies by the same.

        For more information on the adopt-a-method program, please contact the author.
        """
        return packet

    def reset(self):
        """Reset the device, either to recover or prevent fault states on shutdown."""
        self.device = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the connection to the device."""
        pass


class USB(Device):
    def __init__(self, config=1, vendor_id=VENDOR_ID, product_id=PRODUCT_ID):
        super(USB, self).__init__()

        # PyUSB must be available for this device interface
        if usb is None:
            raise ImportError('PyUSB not found.')

        try:
            self.log.debug('Trying to attach USB device {0:x}:{1:x}'.format(vendor_id, product_id))
            device = usb.core.find(idVendor=vendor_id, idProduct=product_id)
        except usb.core.USBError as error:
            raise error

        if device is None:
            raise ValueError('USB device {0:x}:{1:x} not found'.format(vendor_id, product_id))
        self.log.info('Device attached as FL593FL:\n %s', device)
        self.log.info('Resetting...')
        device.reset()

        # May  be unnecessary, as this is not an HID
        try:
            self.log.debug('Attempting to detach kernel driver...')
            device.detach_kernel_driver(0)
            self.log.debug('Kernel driver detached.')
        except BaseException as error:
            # this usually mean that kernel driver had not been attached to being with.
            self.log.debug('Kernel driver detachment failed with {}. No worries.'.format(error))

        try:
            self.log.debug('Setting device configuration: {}'.format(1))
            device.set_configuration(config)
        except usb.core.USBError as error:
            raise error
        except BaseException as error:
            raise error

        assert device is not None
        self.log.debug('Device attachment complete.')
        self.device = device

        # Device configuration to use (FL593FL only has one, i.e. config=1)
        self.config = self.device.get_active_configuration()

        # Device interface, first in configuration tree
        self.interface = self.config[0, 0]

        # Device communication endpoints
        self.endpoint_out, self.endpoint_in = usb.util.find_descriptor(self.interface, find_all=True)
        self.len_receive = self.endpoint_in.wMaxPacketSize
        self.len_transmit = self.endpoint_out.wMaxPacketSize

    def show_configurations(self):
        """Print/log all available configurations."""
        for c, cfg in enumerate(self.device):
            self.log.debug('Configuration %d: %s' % (c, str(cfg.bConfigurationValue)))

    def show_interfaces(self):
        """Print/log all available interfaces."""
        for i, interface in enumerate(self.config):
            self.log.info('Interface %d: %s' % (i, str(interface) + '\n'))

    def show_endpoints(self):
        """Print/log all available endpoints. Not sure this is actually a thing..."""
        # FIXME: Copy'n'paste without change from interfaces... lookup endpoint enumeration!
        raise NotImplementedError
        # for i, interface in enumerate(self.config):
        #     self.log.info('Interface %d: %s' % (i, str(interface) + '\n'))

    def transceive(self, command):
        """Send a command string and receive response."""

        # Write coded command
        try:
            self.endpoint_out.write(encode_command(command))
        except usb.USBError as error:
            self.log.error("Could not write to USB: {:s}".format(error))
            return None
        except ValueError as error:
            self.log.error(error)
            return None

        # Read back result
        try:
            response = self.endpoint_in.read(self.endpoint_in.wMaxPacketSize, TIMEOUT)
        except usb.USBError as error:
            self.log.error("No response: {:s}".format(error))
            return None

        return decode_response(response)

    def test_command(self, command):
        print command

    def close(self):
        if self.device is not None:
            self.device.reset()
            self.device.close()
        self.device = None


class Dummy(Device):
    """Dummy class to allow running the GUI without any device attached.

    Emulates the functionality of a USB or Network attached device.
    """
    def __init__(self):
        super(Dummy, self).__init__()
        self.array = array('B')
        self.array.fromlist([0x00]*EP_PACK_OUT)

    def transceive(self, cmd_packet):
        self.log.debug(repr(cmd_packet))
        return ResponsePacket(self.fake_data(cmd_packet))

    def fake_data(self, packet):
        if packet.op_type == TYPE_READ:
            return self.array
            # data_dict = {
            #     CMD_MODEL: list('Dummy Device'),
            #     CMD_FWVER: list('0.1'),
            #     CMD_CHANCT: [2],
            #     CMD_IMON: [100.0],
            #     CMD_PMON: [50.0],
            #     CMD_LIMIT: [123.0],
            #     CMD_SETPOINT: [120.0],
            #     CMD_MODE: [1],
            #     CMD_ALARM: [FLAG_OFF]*8
            # }
            # pack_list = [DEVICE_TYPE,
            #              packet.channel,
            #              packet.op_type,
            #              packet.op_code]
            # pack_list.extend(data_dict[packet.op_code])
            # self.array.fromlist(,
            #                      ,
            #                      packet.data])
            # return self.array

        if packet.op_type == TYPE_WRITE:
            pack_list = [DEVICE_TYPE, packet.channel, packet.op_type, packet.op_code, ERR_OK]
            pack_list.extend(packet.data)
            pack_list.extend([0x00]*(EP_PACK_OUT-len(pack_list)))
            self.array.fromlist(pack_list)
            return self.array
            # data_dict = {
            #     CMD_LIMIT: 123.0,
            #     CMD_SETPOINT: 120.0,
            #     CMD_MODE: 1,
            #     CMD_ALARM: [FLAG_OFF]*8,
            #     CMD_ENABLE: FLAG_ON
            # }
            # pack_list = [DEVICE_TYPE,
            #              packet.channel,
            #              packet.op_type,
            #              packet.op_code]
            # pack_list.extend()
            # self.array.fromlist()
            # data_dict[packet.op_code],
            #                      packet.data])
            # return self.array


class Socket(Device):
    """Allows control via sockets, e.g. over ethernet to a remote server."""
    def __init__(self, socket_location):
        super(Socket, self).__init__()
        if zmq is None:
            raise ImportError('ZMQ not found.')

        print socket_location

