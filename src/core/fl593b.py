#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 4/5/14 3:27 AM 2013
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

FL593B evaluation board USB interface class
"""

import sys
if sys.hexversion > 0x03000000:
    raise EnvironmentError('Python 3 not supported.')

import time
import threading
import array
import logging
import usb.core
import usb.util

# DEVICE CONSTANTS
VENDOR_ID = 0x1a45
PRODUCT_ID = 0x2001
CONFIGURATION = 1
EP_ADDR_OUT = 0x01
EP_PACK_OUT = 20
EP_ADDR_IN = 0x82
EP_PACK_IN = 21
TIMEOUT = 100  # default timeout of read/write is 1000 ms

# WEISUB protocol constants
# end codes
ERR_OK = 0x00  # no error
ERR_DEVTYPE = 0x01  # device type field incorrect
ERR_CHANNEL = 0x02  # channel number out of range
ERR_OPTYPE = 0x03  # op_type not supported
ERR_NOTIMPL = 0x04  # op_code not implemented
ERR_PENDING = 0x05  # command received, but not completed [ignore data]
ERR_BUSY = 0x06  # device currently busy, has not performed requested op
ERR_DATA = 0x07  # data field content invalid for op_code
ERR_SAFETY = 0x08  # requested op not within safety specs of config
ERR_CALMODE = 0x09  # requested op only available in calibration mode!

# Channels
NUM_CHAN = 2  # (0: device, 1: channel 1, 2: channel 2)

# OpTypes
TYPE_READ = 0x01  # return OpCode quantity to host
TYPE_WRITE = 0x02  # write OpCode  quantity to device
TYPE_MIN = 0x03  # return minimum of OpCode quantity to host
TYPE_MAX = 0x04  # return maximum of OpCode quantity to host

# General OpCodes
# r = read, w = write
CMD_MODEL = 0x00  # r
CMD_SERIAL = 0x01  # rw
CMD_FWVER = 0x02  # r
CMD_DEVTYPE = 0x03  # r
CMD_CHANCT = 0x04  # r
CMD_IDENTIFY = 0x05  # rw
CMD_SAVE = 0x0C  # w
CMD_RECALL = 0x0D  # w
CMD_PASSWD = 0x0E  # rw
CMD_REVERT = 0x0F  # w

# Specific OpCodes (codes > 0x10 device specific)
# r = read, w = write, mm = min/max
CMD_ALARM = 0x10  # r, Alarm flags
CMD_SETPOINT = 0x11  # rwm, Setpoint, units depend on device MODE!
CMD_LIMIT = 0x12  # rwm, current limit (Ampere, applies for CC, CP and analog modulation!)
CMD_MODE = 0x13  # rw, feedback mode
CMD_TRACK = 0x13  # rw, tracking configuration <- ??? what is this?
CMD_IMON = 0x15  # current monitor
CMD_PMON = 0x16  # power monitor
CMD_ENABLE = 0x17  # rw, output enable. Additionally requires the output enable switch
# on the board to be set to EN, and the NT pin to be pulled LOW
CMD_RPD = 0x19  # rwm, kOhm, photodiode feedback resistor for specified channel
CMD_CAL_ISCALE = 0xE2  # rw, current monitor calibration scaling value for selected channel

# ALARM FLAGS
ALARM_FLAG_DICT = {0x00: 'OUT',  # output status. 0: off, 1: on; equals XEN*LEN*REN
                   0x01: 'XEN',  # external enable flag, 0: J102 floating or HIGH, 1: LOW
                   0x02: 'LEN',  # local enable flag, 0: S100 enabled, 0: disabled
                   0x03: 'REN',  # remote enable flag, enable command state
                   0x04: 'MODE1',  # feedback more channel 1, 0: CC, 1: CP
                   0x05: 'MODE2',  # feedback more channel 1, 0: CC, 1: CP
                   0x06: 'PARA',  # parallel mode, state of track command, 0: independently
                   0x07: 'IDENT',  # status identify flag, 0: inactive, 1: active
                   0x08: 'WRITE',  # write to non-volatile memory in progress following SAVE
                   0x09: 'CALMODE'}  # 1: device is in calibration mode, entered with PASSWD,
                                  # and left with REVERT

# DATA (data ignored for types read, min and max)
LEN_DATA = 16  # length data field in bytes

# FLAGS (instead of taking non-zero values as true, uses literal ASCII characters)
# I assume all input gets fed through atoi, sscan or similar?
FLAG_OFF = 0x30  # ASCII 48, '0'
FLAG_ON = 0x31  # ASCII 49, '1'

# TODO: Multiple backend support, e.g. pyusb or libusb-1.0
# TODO: import signal <- signals module!!!
# TODO: Multiple uniquely identifiable devices


class Channel(object):
    _mode = None
    _max = None
    _set = None

    def __init__(self, chan_type=None, name=None):
        self.name = name if name is not None else 'Unknown'
        self.channel_type = chan_type if chan_type is not None else 'control'

        if self.channel_type == 'control':
            self.stuff = 'control stuff'
        else:
            self.stuff = 'laser channel stuff'

    @property
    def mode(self):
        if self._mode is None:
            pass
        else:
            return self._mode

class Packet(object):
    """Represents a USB data packet in the TeamWavelength protocol.

    Can either be a command packet destined for output, or a received response packet.
    In case of a response packet, the received byte array is segmented into the packet
    segments, while a command packet is built from segments given by parameters.
    """
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.dev_type = None
        self.channel = None
        self.op_type = None
        self.op_code = None
        self.end_code = None
        self.data = None
        self.length = 0
        self._packet_array = None

    def __len__(self):
        return self.length

    def __repr__(self):
        if self._packet_array is None:
            return 'No array!!!'
        packet = self._packet_array
        if self.end_code is not None:
            names = ['DevType', 'Channel', 'OpType', 'OpCode', 'EndCode', 'Data']
        else:
            names = ['DevType', 'Channel', 'OpType', 'OpCode', 'Data']
        fields = ['{0:#x}'.format(p) for p in packet[0:len(names)-1]]
        fields.extend([''.join([chr(c) for c in packet[len(names)-1:]])])
        return ''.join(['{0:<7s}: {1:s}\n'.format(n, f) for n, f in zip(names, fields)])

    def __str__(self):
        return str(self._packet_array)

    @property
    def packet(self):
        """String of bytes representing the packet."""
        return self._packet_array


class CommandPacket(Packet):
    """Represents a command packet in the TeamWavelength protocol."""
    def __init__(self, dev_type=0x0, channel=0x0, op_type=TYPE_READ,
                 op_code=CMD_MODEL, data=[0x0]*LEN_DATA, packet_length=EP_PACK_OUT):
        Packet.__init__(self)

        self.dev_type = dev_type
        self.channel = channel
        self.op_type = op_type
        self.op_code = op_code
        self.data = data
        self.length = packet_length

    @property
    def packet(self):
        """String of bytes representing the packet."""
        if self._packet_array is None:
            packet = [self.dev_type, self.channel, self.op_type, self.op_code]
            packet.extend(self.data)

            # add padding if data not covering full length
            if len(packet) < self.length:
                packet.extend([0x00]*(self.length-len(packet)))

            self._packet_array = array.array('B')
            self._packet_array.fromstring(''.join([chr(c) for c in packet]))
        return self._packet_array

    @packet.setter
    def packet(self, byte_array):
        """Command packet has no setter, unless I come up with a smart use for it."""
        pass


class ResponsePacket(Packet):
    """Represents a received byte array in the TeamWavelength protocol."""
    def __init__(self, packet_array):
        Packet.__init__(self)
        assert packet_array
        self.packet = packet_array

    @property
    def packet(self):
        """Byte array of the response"""
        return self._packet_array

    @packet.setter
    def packet(self, packet_array):
        """Chops up response packet and return packet object with new values."""
        self._packet_array = packet_array
        self.dev_type = packet_array[0]
        self.channel = packet_array[1]
        self.op_type = packet_array[2]
        self.op_code = packet_array[3]
        self.end_code = packet_array[4]
        self.data = packet_array[5:]
        self.length = len(packet_array)


class FL593B(object):

    _model = None
    _fwver = None
    _channel_count = None
    _output_enabled = None
    _remote_enabled = None
    _external_enabled = None


    def __init__(self, config=None):
        self.log = logging.getLogger(__name__)
        config = config if config is not None else 1

        # device
        self.device = None
        self.attach(config)
        assert self.device is not None

        # configuration
        self.config = self.device.get_active_configuration()

        # interface
        self.interface = self.config[0, 0]

        # endpoints
        self.endpoint_out, self.endpoint_in = usb.util.find_descriptor(self.interface, find_all=True)
        self.len_receive = self.endpoint_in.wMaxPacketSize
        self.len_transmit = self.endpoint_out.wMaxPacketSize

        self.channels = {0: Channel(chan_type='control', name='Control'),
                         1: Channel(chan_type='laser', name='Channel 1'),
                         2: Channel(chan_type='laser', name='Channel 1')}

        # TODO: That looks like a stupid idea. Maybe separate, then I could iterate over the channels.
        self.control = self.channels[0]
        self.alarms = dict()

    def attach(self, configuration, name=None, vendorId=VENDOR_ID, productID=PRODUCT_ID):
        """Find and attach to the USB device with given vendorID and productID.
        Overly general, as right now there is only one such combination I know of.
        But why not make it neat?
        """
        try:
            self.log.debug('Trying to attach USB device {0:x}:{1:x}'.format(vendorId, productID))
            self.device = usb.core.find(idVendor=vendorId, idProduct=productID)
        except usb.core.USBError as error:
            raise error
        # TODO: search for a particular name
        if self.device is None:
            raise ValueError('Device not found')
        self.log.info('Attached device %s', self.device)


        # Not necessary, as this is not an HID?
        try:
            self.log.info('Attempting to detach kernel driver...')
            self.device.detach_kernel_driver(0)
            self.log.debug('Kernel driver detached.')
        except:  # this usually mean that kernel driver has already been detached
            self.log.debug('Kernel driver detachment failed.')

        self.show_configurations()
        try:
            self.log.debug('Setting device configuration {0:d}'.format(configuration))
            self.device.set_configuration(configuration)
        except usb.core.USBError as error:
            raise error

    def transceive(self, cmd_packet):
        """This method was proudly named by Tim Schroeder, as is generously provided for by cookies of the same.

        For more information on the adopt-a-method program, please contact the author.
        """
        # Write command packet
        try:
            #self.show_packet(cmd_packet)
            bw = self.endpoint_out.write(cmd_packet.packet)
            self.log.debug('{0:d} bytes written'.format(bw))
        except usb.USBError as error:
            raise error

        # Read back result
        try:
            resp_packet = ResponsePacket(self.endpoint_in.read(self.endpoint_in.wMaxPacketSize, 100))
            self.log.debug('{0:d} bytes received'.format(len(resp_packet)))
            #self.show_packet(resp_packet)
        except usb.USBError as error:
            raise error
        return resp_packet

    def show_configurations(self):
        """Print/log all available configurations

        Pretty useless, always returns 1. :D
        """
        for c, cfg in enumerate(self.device):
            self.log.info('Configuration %d: %s' % (c, str(cfg.bConfigurationValue) + '\n'))

    def show_interfaces(self):
        """Print/log all available interfaces

        Not sure this is actually a thing...
        """
        for i, interface in enumerate(self.config):
            self.log.info('Configuration %d: %s' % (i, str(interface) + '\n'))

    def show_endpoints(self):
        """Print/log all available endpoints

        Not sure this is actually a thing...
        """
        for i, interface in enumerate(self.config):
            self.log.info('Configuration %d: %s' % (i, str(interface) + '\n'))

    def show_packet(self, packet):
        """Logs response onto standard output, or logger
        """
        self.log.debug(packet)

    def show_alarms(self, packet=None):
        """Output current state of alarm flag(s)."""
        # TODO: Optionally specify flags.
        # TODO: Optionally hand packet from which to extract flags.

        self.log.info('Alarm flag states:')
        for i in range(10):
            flag = 'ON' if packet[i] == FLAG_ON else 'OFF'
            self.log.info('{0:<20s}: {1:s}\n'.format(ALARM_FLAG_DICT[i], flag))

    def update_alarms(self):
        if self.log is not None:
            self.log.debug('Updating alarm states')
        pass

    # def static_property_decorator(self, device, op_code, dev_type=0x00, channel=0, op_type=TYPE_READ, data=None):
    #     """Decorator for device properties."""
    #     def wrap(prop):
    #         print "Inside wrap()"
    #         assert device is not None
    #         data = None
    #
    #         def transceive(cmd_packet):
    #             cmd_packet = CommandPacket(dev_type, channel, op_type, op_code, data)
    #             rsp_data = device.transceive(cmd_packet)
    #
    #         def wrapped_f(*args):
    #             print "Inside wrapped_f()"
    #             print "Decorator arguments:", arg1, arg2, arg3
    #             prop(*args)
    #             print "After f(*args)"
    #         return wrapped_f
    #
    #     return wrap

    @property
    def is_ready(self):
        return False

    @property
    def output_enable(self):
        """Output enabled when all three enable conditions are met:
        XEN, LEN, REN must be true.
        """
        pass
        #return self.alarms[ALARM_FLAG_DICT[0]]

    @property
    def external_enable(self):
        return self.alarms[ALARM_FLAG_DICT[1]]

    @property
    def local_enable(self):
        return self.alarms[ALARM_FLAG_DICT[2]]

    @property
    def remote_enable(self):
        if self.alarms is None:
            self.update_alarms()
        self.log.debug('Output enabled:')
        return self.alarms[ALARM_FLAG_DICT[3]]

    @remote_enable.setter
    def remote_enable(self, state):
        rsp_packet = self.transceive(CommandPacket(op_type=TYPE_WRITE, op_code=CMD_ENABLE,
                                                   data=[FLAG_ON if state else FLAG_OFF]))
        print repr(rsp_packet)

    @property
    def parallel(self):
        pass

    @property
    def identify(self):
        pass

    @property
    def write(self):
        pass

    @property
    def calibrate(self):
        pass

    @property
    def model(self):
        self.log.debug('Model description:')
        rsp_packet = self.transceive(CommandPacket(op_type=TYPE_READ, op_code=CMD_MODEL))
        return rsp_packet.data.tostring().strip(chr(0))

    @property
    def fwver(self):
        self.log.debug('Firmware version:')
        rsp_packet = self.transceive(CommandPacket(op_type=TYPE_READ, op_code=CMD_FWVER))
        return rsp_packet.data.tostring().strip(chr(0))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    dev = FL593B()
    print repr(dev.model)
    print repr(dev.fwver)
    dev.remote_enable = False
    # run REPL here

    import cmd

    # DO MAGIC!