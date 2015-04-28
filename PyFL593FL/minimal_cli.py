#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 18 Apr 2015 19:53
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

Simple test using string commands to send packets to the fl593fl device.
This would be the new core -- any other interface sends these strings,
which will be translated into the serial packet only at this stage.

Abstraction layers can have their own data structures to represent packets,
as long as the can be transformed into an acceptable command string, and
be constructed from a return string.
"""

import argparse
import logging
from core.Devices import USB, Dummy

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log = logging.getLogger(__name__)

    parser = argparse.ArgumentParser('Mini REPL for FL593FL laser diode driver eval board.')
    parser.add_argument('-d', '--dummy', help='Use dummy device instead of USB connection.', action='store_true')

    cli_args = parser.parse_args()

    device_class = Dummy if cli_args.dummy else USB
    with device_class() as dev:
        # Example usages:
        rsp = dev.transceive("STATUS READ MODEL")
        if rsp:
            print "Response:", rsp

        rsp = dev.transceive("STATUS READ ALARM")
        if rsp:
            print "Response:", rsp

        # Mini REPL
        print "'q' to exit"
        cmd = raw_input(">> ")
        while cmd.upper() != 'Q':
            try:
                rsp = dev.transceive(cmd)
                print "<-", rsp
            except ValueError as error:
                log.debug(error)

            cmd = raw_input(">> ")


