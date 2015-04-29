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

import time
from array import array
from constants import *
from collections import namedtuple
import random
positionals = [CHANNEL_DICT, OP_TYPE_DICT, OP_CODE_DICT]


def encode_command(command):
    # TODO: Checking of proper command sequence?
    command = command.upper()
    try:
        words = command.upper().split(' ')
        assert len(words) >= 3  # at least Channel, OpType and OpCode, data is optional
        code_list = [DEV_TYPE]
        code_list.extend([positionals[pos][word] for pos, word in enumerate(words[0:3])])
        if len(words) > 3:
            code_list.extend(map(ord, " ".join(words[3:])))
        if len(code_list) < EP_PACK_OUT:
            code_list.extend([0x0] * (EP_PACK_OUT-len(code_list)))

    except KeyError:
        raise ValueError("Invalid command: '{}'".format(command))

    encoded = array('B')
    encoded.fromlist(code_list)
    return encoded


def decode_command(command):
    print command
    raise NotImplementedError
    # assert len(command)
    # decoded = command.upper().split(' ')
    # return decoded


def encode_response(response):
    print response
    raise NotImplementedError


def decode_response(response):
    channel = CHANNEL_DICT_REV[response[1]]
    op_type = OP_TYPE_DICT_REV[response[2]]
    op_code = OP_CODE_DICT_REV[response[3]]
    end_code = END_CODE_DICT[response[4]]
    data = response[5:]
    response_string = ' '.join([channel, op_type, op_code, end_code, data.tostring().strip()])
    return response_string


def unpack_string(string, has_end_code=False):
    """Make string into a namedtuple for easier access"""
    try:
        words = list(reversed(string.upper().split(" ")))
        packet = namedtuple("packet", "channel, op_code, op_type, end_code, data, string")
        packet.command = string.upper()
        packet.channel = CHANNEL_DICT[words.pop()]
        packet.op_type = OP_TYPE_DICT[words.pop()]
        packet.op_code = OP_CODE_DICT[words.pop()]
        packet.end_code = END_CODE_DICT_REV[words.pop()] if has_end_code else None
        packet.data = ' '.join(reversed(words))  # rest is data, which may contain spaces
        packet.data = packet.data.strip('\x00')
        packet.string = string
        return packet
    except IndexError:
        raise ValueError("Incomplete packet: {}".format(string))


def memoize_with_expiry(expiry_time=None, _cache=None, num_args=None):
    """Memoization with expiring cache.

    Cache can be external if provided via [_cache] or internal.
    Expiration time will be read from the FL593FL expiry time dictionary if not given. If negative,
    cached values never expire (e.g. constant values like MODEL)"""
    # FIXME: Using keyword argument is separate key from positional argument call
    # to fix: read argument keywords from function and ALWAYS generate the frozen set by sorting them out
    def _decorating_wrapper(func):
        def _caching_wrapper(*args, **kwargs):
            # Determine what cache to use
            if _cache is None and not hasattr(func, '_cache'):
                func._cache = {}
            cache = _cache or func._cache

            mem_args = args[:num_args]
            if kwargs:
                key = mem_args, frozenset(kwargs.iteritems())
            else:
                key = mem_args
            if key in cache:
                result, timestamp = cache[key]
                if expiry_time is None:
                    exp = EXPIRY_DICT[kwargs['op_code'] if 'op_code' in kwargs else args[1]]
                else:
                    exp = expiry_time
                age = time.time() - timestamp
                if exp < 0 or age < exp:
                    return result
            result = func(*args, **kwargs)
            cache[key] = (result, time.time())
            return result
        return _caching_wrapper
    return _decorating_wrapper


@memoize_with_expiry(expiry_time=1.0)
def fake_data(command, chance_to_fail=None, end_code=ERR_OK):
    packet = unpack_string(command)

    channel = packet.channel
    op_type = packet.op_type
    op_code = packet.op_code
    end_code = end_code
    if chance_to_fail is not None and random.random() > chance_to_fail:
        end_code = random.choice(END_CODE_DICT) if end_code is None else end_code
        raise ValueError("Fake failure with error #{}".format(end_code))

    if op_type == TYPE_READ:
        data_dict = {
            CMD_MODEL: 'FL593-Dummy',
            CMD_FWVER: '42.0.0',
            CMD_CHANCT: '2',
            CMD_IMON: "{:.1f}".format(random.random()*120),
            CMD_PMON: "{:.1f}".format(random.random()*120),
            CMD_LIMIT: "{:.1f}".format(random.random()*120),
            CMD_SETPOINT: "{:.1f}".format(random.random()*120),
            CMD_MODE: '1',
            CMD_ALARM: "".join([chr(random.choice([FLAG_OFF, FLAG_ON])) for _ in range(8)])
        }
        data = data_dict[op_code]

    elif op_type == TYPE_WRITE:
        data = packet.data
    else:
        raise NotImplementedError("No fake data for op_type {}".format(op_type))

    return ' '.join(map(str, [CHANNEL_DICT_REV[channel], OP_TYPE_DICT_REV[op_type],
                              OP_CODE_DICT_REV[op_code], END_CODE_DICT[end_code], data]))


if __name__ == "__main__":
    # FIXME: Move into tests
    cmd = "STATUS READ MODEL"
    encoded_cmd = encode_command(cmd)
    print cmd, ':'
    print encoded_cmd, encoded_cmd.tostring().encode('hex')
    print unpack_string(cmd)
    try:
        unpack_string("STATUS READ")  # incomplete command
    except ValueError as error:
        print error
    else:
        raise AssertionError("Should have been illegal string!")

    @memoize_with_expiry(None)
    def read(_):
        return time.time()

    first = read(CMD_IMON)
    cached = read(CMD_IMON)
    time.sleep(0.1)
    expired = read(CMD_IMON)  # should be different!
    print "First: {}\nCached: {}\nExpired: {}".format(first, cached, expired)