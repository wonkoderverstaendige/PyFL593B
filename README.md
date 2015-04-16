#PyFL593FL

Python/PyUSB interface to the [FL593FL](http://www.teamwavelength.com/products/product.php?part=154)  evaluation board for the TeamWavelength [FL500](http://www.teamwavelength.com/products/product.php?part=147) laser diode driver.

<p align="center">
  <img
src="https://github.com/wonkoderverstaendige/PyFL593FL/blob/master/docs/interface_client.png?raw=true"
alt="PyQt4 client screenshot"/>
</p>

USB communication is handled by PyUSB, which can operate with several backends, i.e. libusb-0.1, libusb-1.0 or OpenUSB. Any of these should do the job as the grimy details are thankfully hidden away.

##Windows

To install the driver, use [Zadig](http://zadig.akeo.ie/) and install a libusb-win32 driver as per instructions (For this exact model: vendor id: 0x1a45, product id: 0x2001). Very easy. Then install [PyUSB](https://github.com/walac/pyusb) and done (assuming all the other requirements like PyQt are installed...).

##Linux


###Libusb
Installing on distributions using apt goes something along the lines of:

    $ sudo apt-get install libusb-dev
  
Or for specifically installing libusb-1.0 at the time of writing:

    $ sudo apt-get install libusb-1.0-0-dev

###PyUSB

Many distributions pull the old 0.x branch when using their package manager, but the 1.0.0+ version of PyUSB is
required. As the latter is a pure python library, installing from the github repo should work just fine:

    $ git clone https://github.com/walac/pyusb.git
    $ cd pyusb
    $ python setup.py install
 
 
#Future

Replace the current directly coupled Qt interface with a separate server, handling the USB interface, and a Qt based
client. The two communicate via ZMQ.
