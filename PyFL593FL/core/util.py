#!/usr/bin/env python
# -*- coding: utf-8 -*-

# COMMAND PACKET:
# | Field:   | DevType  | Channel  | OpType  | OpCode  |                     Data                      |
# |----------|----------|----------|---------|---------|-----------------------------------------------|
# | Offset:  |   0  1   |   2  3   |  4  5   |  6  7   | 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 |


# RESPONSE PACKET:
# | Field:   | DevType  | Channel  | OpType  | OpCode  | EndCode  |                      Data                       |
# |----------|----------|----------|---------|---------|----------|-------------------------------------------------|
# | Offset:  |   0  1   |   2  3   |  4  5   |  6  7   |   8  9   | 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 |

# EXAMPLE
# "STATUS READ MODULE"

from array import array
from constants import *
from itertools import chain
positionals = [CHANNEL_DICT, OP_TYPE_DICT, OP_CODE_DICT]


def encode_command(command):
    # TODO: Checking of proper command sequence?
    assert len(command) >= 3  # at least Channel, OpType and OpCode, data is optional
    try:
        words = command.upper().split(' ')
        code_list = [DEV_TYPE]
        code_list.extend([positionals[pos][word] for pos, word in enumerate(words)])
        if len(code_list) < EP_PACK_OUT:
            code_list.extend([0x0] * (EP_PACK_OUT-len(code_list)))

    except KeyError:
        print "INVALID COMMAND!"
        return None
    encoded = array('B')
    encoded.fromlist(code_list)
    return encoded


def decode_command(command):
    raise NotImplementedError
    # assert len(command)
    # decoded = command.upper().split(' ')
    # return decoded


def encode_response(response):
    raise NotImplementedError


def decode_response(response):
    # self.dev_type = byte_array[1]
    # self.channel = byte_array[3]
    # self.op_type = byte_array[5]
    # self.op_code = byte_array[7]
    # self.end_code = byte_array[9]
    # self.data = byte_array[10:]
    channel = response[1]
    op_type = response[2]
    op_code = response[3]
    end_code = response[4]
    data = response[5:]

    print response.tostring().encode('hex'), 'raw:', response.tostring()
    print channel, CHANNEL_DICT_REV[channel]
    print op_type, OP_TYPE_DICT_REV[op_type]
    print op_code, OP_CODE_DICT_REV[op_code]
    print end_code, END_CODE_DICT_REV[end_code]
    return ' '.join([CHANNEL_DICT_REV[channel], OP_TYPE_DICT_REV[op_type],
                     OP_CODE_DICT_REV[op_code], END_CODE_DICT_REV[end_code]])

if __name__ == "__main__":
    cmd = "STATUS READ MODEL"
    ecmd = encode_command(cmd)
    print cmd, ':', ecmd, len(ecmd), ecmd.tostring().encode('hex')


# Data Field Formatting
#
# The data field for any given command or response packet is a 16-byte buffer that can be applied as needed by any
# function provided by a particular device. The data field should be used to transfer data by means that are platform
# independent to avoid the need to manage byte-ordering within the data field. There are four primary types of data that
# can be transferred in the data field: string, numeric, boolean and bitmapped.
#
# String data allows for the transfer of data that contains characters that cannot be interpreted or represented as
# numeric data. This includes the characters A-Z, a-z, punctuation marks and whitespace. String data is used to
# represent the model number, serial number and possibly the firmware version. All data in a string data field are
# left-aligned, and unused bytes in the data field must be padded with NULL characters (ASCII 0).
#
# Numeric data is any data that can be evaluated as or converted to numeric form. This includes all real numbers.
# Any measured quantities, such as current monitors, temperature monitors and power monitors all will return unitless
# values in the data field, however this value will be scaled to units of the quantity measured. For example, if a
# laser driver's current monitor is set to 100mA, the data field when requesting the current monitor value will
# be represented in units of amperes. Similarly, photodiode current will be represented in amps for
# laser drivers. Temperature controllers will have the option of representing temperatures in either volts or degrees
# Celsius, since converting the measured feedback in volts to degrees Celsius cannot be done without additional
# information about the temperature sensor that the user may not possess or may not be readily available.
#
# Boolean data represents a single boolean term. The data field will use left-aligned data within the data field,
# and only the left-most character will contain data. The remaining characters may contain additional information,
# however it will be ignored. See the data sheet for specific USB based products to see which commands utilize boolean
# data. With a boolean term, a value of zero indicates a logical false, and a nonzero value indicates true.

# The final data format is the bitmapped format. The bitmapped type is similar to boolean, except that it utilizes all
# 16 of the data field characters instead of just the first (position 0). Just as with the boolean type, each character
# within the bitmap field is represented either as a '0' (ASCII 48) or any other numerical character, including '1'
# (ASCII 49) through '9' (ASCII 57). This is useful for commands such as the ALARM command, where multiple boolean
# values such as output state, enabled state, interlock state and limit flags are transferred at one time. A value of
# '0' in any given character indicates a logical false, and any other numeric value from '1' to '9' (inclusive) are
# considered to be a logical true. Any other character is considered illegal, and command packets containing any other
# characters will return a response packet with an end code of ERR_DATA. This allows up to 16 boolean quantities to be
# transferred in a bitmapped data transfer.