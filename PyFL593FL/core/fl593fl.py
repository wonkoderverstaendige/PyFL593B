#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 05 Apr 2014 3:27 AM
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

FL593FL evaluation board USB interface class
"""

import sys
import logging
from collections import namedtuple
import Devices
from Channels import StatusChannel, LaserChannel

if sys.hexversion > 0x03000000:
    raise EnvironmentError('Python 3 not supported.')


class FL593FL(object):
    def __init__(self, device_class=Devices.USB, config=1):
        self.log = logging.getLogger(self.__class__.__name__)
        self.channels = None
        self.status = None

        try:
            device = device_class(config)
            self.log.debug("Using device class {}".format(device_class))
        except (ValueError, ImportError) as error:
            self.log.error('Device not instantiated: {}'.format(error))
            return

        assert device is not None
        self.device = device

        self.log.debug('Initializing device proxy channels...')
        # The general control/status channel and diode driver channels
        # Channel 0: Status channel, device status, modes, general information
        # Channels 1-2: Laser channels if in independent mode, otherwise only channel 1
        channels = namedtuple('channels', 'status, ld1, ld2')
        self.channels = channels(StatusChannel(0), LaserChannel(1), LaserChannel(2))
        self.status = self.channels.status
        self.initialize()
        self.update()
        self.log.debug('Device proxy channels initialized and ready to go.')

    def initialize(self):
        for channel in self.channels:
            channel.initialize(self.device)

    def update(self):
        """Ask the channels to ask the device to grab the respective current states."""
        for channel in self.channels:
            channel.update()

    def reset(self):
        """Reset whole device.

        Seems to fix problems where USB device becomes unresponsive, especially
        when previous interaction failed or was disrupted mid-transfer,leaving packets
        floating around in buffers.
        """
        self.device.reset()

    def close(self):
        for channel in self.channels:
            channel.close()
        self.device.close()
        del self.device


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--DEBUG', action='store_true', help='Print more!')
    parser.add_argument('--DUMMY', action='store_true', help='Initiate with dummy device interface sending \
                        random values. Useful for GUI debugging or when user forgot device in the workshop.')
    cli_args = parser.parse_args()

    log_level = logging.DEBUG if cli_args.DEBUG else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    dev = FL593FL(device_class=Devices.Dummy if cli_args.DUMMY else Devices.USB)
    if dev is not None and dev.channels.status is not None:
        print 'Device:', dev.channels.status.get_device_type()
        print 'Model:', dev.channels.status.get_model()
        print 'Firmware:', dev.channels.status.get_fw_version()
        dev.channels.status.show_alarms()
        dev.close()
