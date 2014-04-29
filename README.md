PyFL593FL
==========

Python/PyUSB interface to the FL593FL evaluation board for the TeamWavelength FL500 laser diode driver.


Installation
==============

libusb
------

    $ sudo apt-get install libusb

PyUSB
-----

Many distributions pull the old 0.x branch when using their package manager, but the 1.0.0+ version of PyUSB is required. As the latter is a pure python library, installing from the github repo should work just fine:

    $ git clone https://github.com/walac/pyusb.git
    $ cd pyusb
    $ python setup.py install
 
 
Future
======

PyQt interface (maybe test the fancy new QML stuff?)
