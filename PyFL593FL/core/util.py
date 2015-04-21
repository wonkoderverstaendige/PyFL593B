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
    command = command.upper()
    try:
        words = command.upper().split(' ')
        code_list = [DEV_TYPE]
        code_list.extend([positionals[pos][word] for pos, word in enumerate(words)])
        if len(code_list) < EP_PACK_OUT:
            code_list.extend([0x0] * (EP_PACK_OUT-len(code_list)))

    except KeyError:
        raise ValueError("Invalid command: '{}'".format(command))

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
    channel = CHANNEL_DICT_REV[response[1]]
    op_type = OP_TYPE_DICT_REV[response[2]]
    op_code = OP_CODE_DICT_REV[response[3]]
    end_code = END_CODE_DICT[response[4]]
    data = response[5:]

    return ' '.join([channel, op_type, op_code, end_code, data.tostring().strip()])

if __name__ == "__main__":
    cmd = "STATUS READ MODEL"
    ecmd = encode_command(cmd)
    print cmd, ':', ecmd, len(ecmd), ecmd.tostring().encode('hex')
