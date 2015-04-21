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

from core.Devices import USB

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    dev = USB()

    # EXAMPLE:
    rsp = dev.transceive("STATUS READ MODEL")
    if rsp:
        print "Response:", rsp

    print "'q' to exit"
    cmd = raw_input(">> ")
    while cmd.upper() != 'Q':
        if rsp:
            print "Response:", rsp
        rsp = dev.transceive(cmd)
        cmd = raw_input(">> ")


