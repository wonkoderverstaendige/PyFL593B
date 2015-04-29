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
from constants import *
import util
try:
    import usb
except ImportError:
    usb = None

try:
    import zmq
except ImportError:
    zmq = None


class Device(object):
    """Generic device interface class."""
    def __init__(self):
        logging.addLevelName(LOG_LVL_VERBOSE, "VERBOSE")
        self.log = logging.getLogger(__name__)
        self.len_transmit = None
        self.len_receive = None
        self.device = None
        self.num_channels = MAX_NUM_CHAN

    def __enter__(self):
        return self

    def open(self, *args, **kwargs):
        """Open connection to device."""
        self.device = None

    def transceive(self, command):
        """This method was aptly named by Tim Schroeder, and is generously provided for with cookies by the same.

        For more information on the adopt-a-method program, please contact the author.
        """
        return command

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
            raise ImportError('PyUSB not found. See README.md for instructions.')

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
        assert self.endpoint_in.wMaxPacketSize == EP_PACK_IN
        assert self.endpoint_out.wMaxPacketSize == EP_PACK_OUT

    def _show_configurations(self):
        """Print/log all available configurations."""
        for c, cfg in enumerate(self.device):
            self.log.debug('Configuration %d: %s' % (c, str(cfg.bConfigurationValue)))

    def _show_interfaces(self):
        """Print/log all available interfaces."""
        for i, interface in enumerate(self.config):
            self.log.info('Interface %d: %s' % (i, str(interface) + '\n'))

    def _show_endpoints(self):
        """Print/log all available endpoints. Not sure this is actually a thing..."""
        # FIXME: Copy'n'paste without change from interfaces... lookup endpoint enumeration!
        self.log.error("Shouldn't be called by anyone!")
        raise NotImplementedError

    def transceive(self, command):
        """Send a command string and receive response."""
        # Write coded command
        encoded_command = util.encode_command(command)
        self.log.log(LOG_LVL_VERBOSE, "Command: {}, encoded: {}".format(command, encoded_command))
        try:
            self.endpoint_out.write(encoded_command)
        except usb.USBError as error:
            self.log.error("Could not write to USB: {:s}".format(error))
            raise error
        except ValueError as error:
            self.log.error(error)
            raise error

        # Read back result
        try:
            response = self.endpoint_in.read(EP_PACK_IN, TIMEOUT)
        except usb.USBError as error:
            self.log.error("No response: {:s}".format(error))
            raise error
        self.log.log(LOG_LVL_VERBOSE, "Response: {}, encoded: {}".format(util.decode_response(response), response))

        return util.decode_response(response)

    def close(self):
        if self.device is not None:
            self.device.reset()
        self.device = None


class Dummy(Device):
    """Dummy class to allow running the GUI without any device attached.

    Emulates the functionality of a USB or Network attached device.
    """
    def __init__(self):
        super(Dummy, self).__init__()

    def transceive(self, command):
        return util.fake_data(command)


class Socket(Device):
    """Allows control via sockets, e.g. over ethernet to a remote server."""
    def __init__(self, socket_location):
        super(Socket, self).__init__()
        if zmq is None:
            raise ImportError('ZMQ not found.')

        print socket_location

