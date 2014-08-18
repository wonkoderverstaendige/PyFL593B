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
        self.log = logging.getLogger(self.__class__.__name__)
        self.channels = None
        self.status = None

        try:
            # select device interface backend
            self.log.debug("Using device class %s" % device_interface.upper())
            if device_interface == 'usb':
                self.device = Devices.USB(config)  # defaults to config 1
            elif device_interface == 'dummy':
                self.device = Devices.Dummy()
            elif device_interface == 'zmq':
                self.device = Devices.Socket('socket:port')
            else:
                raise NotImplementedError
        except (ValueError, ImportError) as error:
            self.log.error('Device not instantiated: {}'.format(error))
            return

        assert self.device is not None

        self.log.debug('Initializing device proxy channels...')
        # The general control/status channel and diode driver channels
        # Channel 0: Status channel, device status, modes, general information
        # Channels 1-2: Laser channels if in independent mode, otherwise only channel 1
        status_channel = StatusChannel(self)
        try:
            status_channel.initialize(self.device)
        except BaseException, error:
            self.log.error(error)
            return

        self.status = status_channel
        self.channels = {n: self.status if n == 0 else LaserChannel(chan_num=n)
                         for n in range(self.device.num_channels+1)}
        self.log.debug('Device proxy channels initiated.')

    def update(self):
        """Ask the channels to ask the device to grab the respective current states."""
        for channel in self.channels.values():
            channel.update()

    def reset(self):
        """Reset whole device.

        Seems to fix problems where USB device becomes unresponsive, especially
        when previous interaction failed or was disrupted mid-transfer,leaving packets
        floating around in buffers.
        """
        self.device.reset()

    def close(self):
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
    if dev is not None and dev.status is not None:
        print 'Device:', dev.status
        print 'Model:', dev.status.get_model()
        print 'Firmware:', dev.status.get_fw_version()
        dev.status.show_alarms()
        dev.close()
