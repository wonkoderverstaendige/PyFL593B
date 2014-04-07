# -*- coding: utf-8 -*-
"""
Created on 4/5/14 3:31 AM 2013
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

GUI controlling PyFL593B interface instance
"""

__version__ = '0.0.1'

import sys
if sys.hexversion > 0x03000000:
    raise EnvironmentError('Python 3 not supported.')

from core.fl593b import FL593B
import ui

dev = FL593B()
