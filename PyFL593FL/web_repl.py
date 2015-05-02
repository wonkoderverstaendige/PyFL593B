#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 21 Apr 2015 21:40
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

Run webserver connecting to USB, send command/response from/to browser via websocket.
"""

import argparse
import logging
from web.web_repl.server import main
from core.Devices import USB, Dummy
from core.constants import LOG_LVL_VERBOSE

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Mini REPL for FL593FL laser diode driver eval board.')
    parser.add_argument('-d', '--dummy', help='Use dummy device instead of USB connection.', action='store_true')
    parser.add_argument('-v', '--verbose', help='Enable packet-level logging.', action='store_true')
    parser.add_argument('-p', '--port', help="Port for web server.")

    cli_args = parser.parse_args()

    logging.addLevelName(LOG_LVL_VERBOSE, "VERBOSE")
    logging.basicConfig(level=LOG_LVL_VERBOSE if cli_args.verbose else logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log = logging.getLogger(__name__)

    device_class = Dummy if cli_args.dummy else USB

    with device_class() as dev:
        # FIXME: Pass on parameters (e.g. port)
        main(dev)
