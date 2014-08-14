# -*- coding: utf-8 -*-
"""
Created on 08 Apr 2014 2:22 PM
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

"""

import array
import logging
from fl593fl_constants import *


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
        packet = self.packet
        if packet is None:
            return 'No array!!!'
        if self.end_code is not None:
            names = ['DevType', 'Channel', 'OpType', 'OpCode', 'EndCode', 'Data']
        else:
            names = ['DevType', 'Channel', 'OpType', 'OpCode', 'Data']
        fields = ['{0:#x}'.format(p) for p in packet[0:len(names)-1]]
        fields.extend([''.join([chr(c) for c in packet[len(names)-1:]])])
        return ''.join(['{0:<7s}: {1:s}\n'.format(n, f) for n, f in zip(names, fields)])

    def __str__(self):
        if self.packet is not None:
            return self.packet.tostring().strip(chr(0))

    @property
    def packet(self):
        """String of bytes representing the packet."""
        return self._packet_array

    @property
    def data_str(self):
        return None if self.data is None else self.data.tostring().strip(chr(0))


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
        """Array of bytes representing the packet."""
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