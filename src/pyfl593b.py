#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 4/5/14 3:31 AM 2013
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

GUI controlling PyFL593B interface instance
"""

__version__ = '0.1.0'

import logging
import sys
if sys.hexversion > 0x03000000:
    raise EnvironmentError('Python 3 not supported.')
from core.fl593b import FL593B


def main(*args, **kwargs):
    pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Command line parsing

    main()