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
from fl593fl_constants import *
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

    def open(self, *args, **kwargs):
        """Open connection to device."""
        self.device = None

    def transceive(self, packet):
        """Send a piece of data and return the response."""
        return packet

    def reset(self):
        """Reset the device, either to recover or prevent fault states on shutdown."""
        self.device = None

    def close(self):
        """Close the connection to the device."""
        if self.device is not None:
            self.device.close()


class FL593FL_USB(Device):
    def __init__(self, config=1, idVendor=VENDOR_ID, idProduct=PRODUCT_ID):
        super(FL593FL_USB, self).__init__()

        # PyUSB must be available for this device interface
        if usb is None:
            raise ImportError('PyUSB not found.')

    # def open(self, configuration):
    #     """Find and attach to the USB device with given vendorID and productID.
    #     Overly general, as right now there is only one such combination I know of.
    #     But why not make it neat?
    #     """
        try:
            self.log.debug('Trying to attach USB device {0:x}:{1:x}'.format(idVendor, idProduct))
            device = usb.core.find(idVendor=idVendor, idProduct=idProduct)
        except usb.core.USBError as error:
            raise error
        # TODO: search for a particular name
        if device is None:
            raise ValueError('Device not found')
        self.log.info('Attached to USB device %s as FL593FL', device)

        # May  be unnecessary, as this is not an HID
        try:
            self.log.debug('Attempting to detach kernel driver...')
            device.detach_kernel_driver(0)
            self.log.debug('Kernel driver detached.')
        except BaseException as error:
            print error
            # this usually mean that kernel driver had not been attached to being with.
            self.log.debug('Kernel driver detachment failed. No worries.')

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

    def transceive(self, cmd_packet):
        """This method was aptly named by Tim Schroeder, and is generously provided for with cookies by the same.

        For more information on the adopt-a-method program, please contact the author.
        """
        # Write command packet
        try:
            bw = self.endpoint_out.write(cmd_packet.packet)
            #self.log.debug('{0:d} bytes written: {1:s}'.format(bw, str(cmd_packet)))
        except usb.USBError as error:
            self.log.error("Could not write to USB! {:s}".format(error))
            return None

        # Read back result
        try:
            resp_packet = ResponsePacket(self.endpoint_in.read(self.endpoint_in.wMaxPacketSize, TIMEOUT))
            #self.log.debug('{0:d} bytes received: {1:s}'.format(len(resp_packet), str(resp_packet)))
            #self.show_packet(resp_packet)
        except usb.USBError as error:
            self.log.error("Could not receive response! {:s}".format(error))
            return None

        return resp_packet


class FL593FL_Dummy(Device):
    """Dummy class to allow running the GUI without any device attached.

    Emulates the functionality of a USB or Network attached device.
    """
    def __init__(self):
        super(FL593FL_Dummy, self).__init__()


class FL593FL_Socket(Device):
    """Allows control via sockets, e.g. over ethernet to a remote server."""
    def __init__(self, socket_location):
        super(FL593FL_Socket, self).__init__()
        if zmq is None:
            raise ImportError('ZMQ not found.')

        print socket_location

