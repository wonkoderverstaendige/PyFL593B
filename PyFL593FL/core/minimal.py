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

from util import encode_command, decode_response
from Devices import USB

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    dev = USB()
    cmd = encode_command("STATUS READ MODEL")
    print "{}Bytes Data: {}".format(len(cmd), cmd.tostring().encode('hex'))
    rsp = dev.transceive("STATUS READ MODEL")
    if rsp:
        print "Response:", decode_response(rsp)

    cmd = encode_command("STATUS READ CHANCT")
    print "{}Bytes Data: {}".format(len(cmd), cmd.tostring().encode('hex'))
    rsp = dev.transceive("STATUS READ CHANCT")
    if rsp:
        print "Response:", decode_response(rsp)