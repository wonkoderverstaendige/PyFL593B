# -*- coding: utf-8 -*-
"""
Created on 08 Apr 2014 2:22 PM
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

"""

import logging
from array import array
from fl593fl_constants import *


class Packet(object):
    """Represents a USB data packet in the TeamWavelength protocol.

    Can either be a command packet destined for output, or a received response packet.
    In case of a response packet, the received byte array is segmented into the packet
    segments, while a command packet is built from segments given by parameters.
    """
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.dev_type = None  # constant for FL593FL
        self.channel = None   # channel sending/receiving packet
        self.op_type = None   # type of operation to perform (read, write...)
        self.op_code = None   # target register (set point,
        self.end_code = None  # only used by response packet, return value of operation
        self.data = None      # used by or returned from operation
        self._array = None    # the array representation

    def __len__(self):
        """Number of bytes in full array, including op-codes and data."""
        return len(self.get_array()) if self.get_array() is not None else 0

    def __repr__(self):
        """Verbose string representation of packet content with full field names."""
        if self.get_array() is None:
            return 'Packet is empty'
        if self.end_code is None:
            names = ['DevType', 'Channel', 'OpType', 'OpCode', 'Data']
        else:
            names = ['DevType', 'Channel', 'OpType', 'OpCode', 'EndCode', 'Data']
        fields = ['{0:#x}'.format(p) for p in self.get_array()[0:len(names)-1]]
        fields.extend([''.join([chr(c) for c in self.get_array()[len(names)-1:]])])
        full_fields = ''.join(['{0:<7s}: {1:s}\n'.format(n, f) for n, f in zip(names, fields)])
        return "Packet " + self.__class__.__name__ + ':\n' + full_fields

    def __str__(self):
        """Bare string representation of packet array content.
        May contain un-human-readable whitespaces.
        """
        return '--EMPTY--' if self._array is None else self.get_array().tostring().strip(chr(0))

    def to_string(self, verbose=False):
        # FIXME: Verbosity control of string representation
        # I.e. expand the numerical values (0x1 -> Channel 1, etc)
        if not verbose:
            return str(self)
        else:
            return "THIS IS A LONG STRING!!!"

    def get_array(self):
        """Return array of bytes representing the packet as transmitted to the USB device."""
        return self._array

    def set_array(self, byte_array):
        """Return array of bytes representing the packet as transmitted to the USB device."""
        self._array = byte_array

    def data_str(self):
        """String of only the data field. Trailing whitespaces (nulls) removed."""
        return 'empty' if self.data is None else str(self.data).strip(chr(0))


class CommandPacket(Packet):
    """Represents a command packet in the TeamWavelength protocol.

    The array will be sent to the device, to change or inquire the
    status of a register.
    """
    def __init__(self, dev_type=DEVICE_TYPE,
                 channel=CHAN_STATUS,
                 op_type=TYPE_READ,
                 op_code=CMD_MODEL,
                 data=[0x0]*LEN_DATA,
                 packet_length=EP_PACK_OUT):
        super(CommandPacket, self).__init__()

        self.dev_type = dev_type
        self.channel = channel
        self.op_type = op_type
        self.op_code = op_code
        self.data = data
        self.required_array_length = packet_length  # to pad with NULLs

    def get_array(self):

        # if array doesn't exist yet, build it by values given in init
        if self._array is None:
            self.log.debug('Building array from scratch')
            packet = [self.dev_type, self.channel, self.op_type, self.op_code]
            packet.extend(self.data)

            # add padding if data not covering full length
            if len(packet) < self.required_array_length:
                packet.extend([0x0] * (self.required_array_length-len(packet)))

            self._array = array('B')
            self._array.fromlist(packet)
        return self._array


class ResponsePacket(Packet):
    """Represents a received byte array in the TeamWavelength protocol as returned
    in response to a command packet.
    """
    def __init__(self, byte_array):
        super(ResponsePacket, self).__init__()
        assert byte_array
        self.set_array(byte_array)

        self.dev_type = byte_array[0]
        self.channel = byte_array[1]
        self.op_type = byte_array[2]
        self.op_code = byte_array[3]
        self.end_code = byte_array[4]
        self.data = byte_array[5:]
