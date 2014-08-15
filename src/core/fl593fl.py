#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 05 Apr 2014 3:27 AM
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

FL593FL evaluation board USB interface class
"""

import sys
import logging
import Devices
from Channels import StatusChannel, LaserChannel

if sys.hexversion > 0x03000000:
    raise EnvironmentError('Python 3 not supported.')


class FL593FL(object):
    def __init__(self, device_interface, config=1):
        self.log = logging.getLogger(__name__)

        # attach to device with configuration (default: 1)
        if device_interface == 'usb':
            self.device = Devices.FL593FL_USB(config)
        elif device_interface == 'dummy':
            self.device = Devices.FL593FL_Dummy()
        elif device_interface == 'zmq':
            self.device = Devices.FL593FL_Socket('socket:port')
        else:
            raise NotImplementedError
        assert self.device is not None

        self.status = None

        self.log.debug('Initializing device proxy channels...')

        # The general control/status channel and diode driver channels
        self.channels = {n: LaserChannel(channel_number=n) if n else StatusChannel(self)
                         for n in range(self.device.num_channels+1)}  # +1 for status channel (channel 0)
        self.status = self.channels[0]
        self.status.initialize(self.device)
        self.log.debug('Device proxy channels initiated.')

    def update(self):
        """Ask the channels to ask the device to grab the respective current states."""
        for channel in self.channels.values():
            channel.update()

    def show_packet(self, packet):
        """Show formatted packet content. Rather useful for debugging."""
        # TODO: Pull in description of field values.
        self.log.info(repr(packet))

    def show_alarms(self):
        """Output current state of alarm flag(s)."""
        self.status.show_alarms()

    @property
    def model(self):
        self.log.debug('Model description:')
        return self.status.model

    @property
    def fwver(self):
        self.log.debug('Firmware version:')
        return self.status.fwver

    @property
    def num_channels(self):
        self.log.debug('Channel count:')
        return self.status.num_channels

    @property
    def serial(self):
        self.log.debug('Serial number:')
        return self.status.serial

    def reset(self):
        """Reset whole device.

        Seems to fix problems where USB device becomes unresponsive, especially
        when previous interaction failed or was disrupted mid-transfer,leaving packets
        floating around in buffers.
        """
        self.device.reset()

    def close(self):
        # disable and zero channel controls
        self.status.close()
        for key in self.channels:
            self.channels[key].close()

        # Sometimes the device got stuck, this MAY have solved it!
        self.device.reset()
        del self.device


if __name__ == '__main__':
    # CLI
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--DEBUG', action='store_true', help='Print more!')
    parser.add_argument('--DUMMY', action='store_true', help='Initiate with dummy device interface sending \
                        random values. Useful for GUI debugging or when user forgot device in the workshop.')
    cli_args = parser.parse_args()

    log_level = logging.DEBUG if cli_args.DEBUG else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    dev = FL593FL(device_interface='dummy' if cli_args.DUMMY else 'usb')
    print 'Model:', dev.model
    print 'Firmware:', dev.fwver
    dev.show_alarms()
    dev.close()
