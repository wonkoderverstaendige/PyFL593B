#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 21 Apr 2015 21:40
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

Run webserver connecting to USB, send command/response from/to browser via websocket.
"""

from web.server import main
from core.Devices import USB

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    dev = USB()

    main(dev)