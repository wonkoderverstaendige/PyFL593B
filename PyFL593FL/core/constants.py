# -*- coding: utf-8 -*-
"""
Created on 08 Apr 2014 1:48 PM
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

Constants used by the FL593FL device class. From the WeiUSB documentation
provided by TeamWavelength
http://www.teamwavelength.com/permanent/usb/docs/api/weiprot.html
and the FL593FL data sheet:
http://www.teamwavelength.com/downloads/datasheets/fl593.pdf

Note: all codes are < 0x00FF, so the first Byte of each field (other than data) is always 0!
"""

# DEVICE BEHAVIOR
TIMEOUT = 100  # default timeout of read/write is 100 ms

AUTO_START_ZERO_SET = True  # For safety reasons, try to disable
AUTO_START_ZERO_LIMIT = True  # For safety reasons, try to zero
START_REMOTE_ENABLE_STATE = False  # Set to state on startup

AUTO_EXIT_ZERO_SET = True  # For safety reasons, try to disable
AUTO_EXIT_ZERO_LIMIT = True  # For safety reasons, try to zero
EXIT_REMOTE_ENABLE_STATE = False  # For safety reasons, disable on exit

# WEIUSB protocol constants ACCORDING TO DOCUMENTATION! BEWARE, SEE NOTE BELOW TABLES!

# COMMAND PACKET:
# | Field:   | DevType  | Channel  | OpType  | OpCode  |                     Data                      |
# |----------|----------|----------|---------|---------|-----------------------------------------------|
# | Offset:  |   0  1   |   2  3   |  4  5   |  6  7   | 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 |


# RESPONSE PACKET:
# | Field:   | DevType  | Channel  | OpType  | OpCode  | EndCode  |                      Data                       |
# |----------|----------|----------|---------|---------|----------|-------------------------------------------------|
# | Offset:  |   0  1   |   2  3   |  4  5   |  6  7   |   8  9   | 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 |

##### !!! Contrary to documentation, fields other than "Data" are only of size 1 (Byte), not 2!!! This means all
##### !!! offsets are wrong.

# DEVICE CONSTANTS
VENDOR_ID = 0x1a45
PRODUCT_ID = 0x2001
DEV_TYPE = 0x0000
CONFIGURATION = 1
MAX_CONN_RETRIES = 10
EP_ADDR_OUT = 0x01
EP_PACK_OUT = 20  # length bytes to send
EP_ADDR_IN = 0x82
EP_PACK_IN = 21  # length bytes returned

# CHANNELS
MAX_NUM_CHAN = 2
CHAN_STATUS = 0x0000
CHAN_LD1 = 0x0001
CHAN_LD2 = 0x0002
CHANNEL_DICT = {
    'STATUS': CHAN_STATUS,
    'LD1': CHAN_LD1,
    'LD2': CHAN_LD2,
}
CHANNEL_DICT_REV = {v: k for k, v in CHANNEL_DICT.iteritems()}

# OpTypes
TYPE_READ = 0x0001  # return OpCode quantity to host
TYPE_WRITE = 0x0002  # write OpCode  quantity to device
TYPE_MIN = 0x0003  # return minimum of OpCode quantity to host
TYPE_MAX = 0x0004  # return maximum of OpCode quantity to host
OP_TYPE_DICT = {
    "READ": TYPE_READ,
    "WRITE": TYPE_WRITE,
    "MIN": TYPE_MIN,
    "MAX": TYPE_MAX,
}
OP_TYPE_DICT_REV = {v: k for k, v in OP_TYPE_DICT.iteritems()}

# General OpCodes
# r = read, w = write
CMD_MODEL = 0x0000  # r
CMD_SERIAL = 0x0001  # rw
CMD_FWVER = 0x0002  # r
CMD_DEVTYPE = 0x0003  # r
CMD_CHANCT = 0x0004  # r
CMD_IDENTIFY = 0x0005  # rw
CMD_SAVE = 0x000C  # w
CMD_RECALL = 0x000D  # w
CMD_PASSWD = 0x000E  # rw
CMD_REVERT = 0x000F  # w
# Specific OpCodes (codes > 0x10 device specific)
# r = read, w = write, mm = min/max
CMD_ALARM = 0x0010  # r, Alarm flags
CMD_SETPOINT = 0x0011  # rwm, Setpoint, units depend on device MODE!
CMD_LIMIT = 0x0012  # rwm, current limit (Ampere, applies for CC, CP and analog modulation!)
CMD_MODE = 0x0013  # rw, feedback mode
CMD_TRACK = 0x0014  # rw, tracking configuration (independent: 0/parallel: 1)
CMD_IMON = 0x0015  # current monitor
CMD_PMON = 0x0016  # power monitor
CMD_ENABLE = 0x0017  # rw, output enable. Additionally requires the output enable switch
# on the board to be set to EN, and the NT pin to be pulled LOW
CMD_RPD = 0x0019  # rwm, kOhm, photodiode feedback resistor for specified channel
CMD_CAL_ISCALE = 0x00E2  # rw, current monitor calibration scaling value for selected channel
OP_CODE_DICT = {
    'MODEL': CMD_MODEL,
    'SERIAL': CMD_SERIAL,
    'FWVER': CMD_FWVER,
    'DEVTYPE': CMD_DEVTYPE,
    'CHANCT': CMD_CHANCT,
    'IDENTIFY': CMD_IDENTIFY,
    'SAVE': CMD_SAVE,
    'PASSWD': CMD_PASSWD,
    'REVERT': CMD_REVERT,
    'RECALL': CMD_RECALL,
    'ALARM': CMD_ALARM,
    'SETPOINT': CMD_SETPOINT,
    'LIMIT': CMD_LIMIT,
    'MODE': CMD_MODE,
    'TRACK': CMD_TRACK,
    'IMON': CMD_IMON,
    'PMON': CMD_PMON,
    'ENABLE': CMD_ENABLE,
    'RPD': CMD_RPD,
    'CAL_ISCALE': CMD_CAL_ISCALE,
}
# TODO: Expiring memoization to priorize updating quickly changing values
# Should make access of properties from the GUI less painful
# but cap request rate to 10 ms, i.e. ~ once per > 60fps refresh
# should allow to read from memoized channels withhout having to worry about
# repeated accesses and keeping them up-to-date internally
# see utils.py:memoize_with_expiry decorator
EXPIRY_NEVER = -1.0
EXPIRY_FAST = 0.010
EXPIRY_IMMEDIATE = 0.0
EXPIRY_DICT = {
    CMD_MODEL: EXPIRY_NEVER,
    CMD_SERIAL: EXPIRY_NEVER,
    CMD_FWVER: EXPIRY_NEVER,
    CMD_DEVTYPE: EXPIRY_NEVER,
    CMD_CHANCT: EXPIRY_NEVER,
    CMD_IDENTIFY: EXPIRY_IMMEDIATE,
    CMD_SAVE: EXPIRY_IMMEDIATE,
    CMD_PASSWD: EXPIRY_IMMEDIATE,
    CMD_REVERT: EXPIRY_IMMEDIATE,
    CMD_RECALL: EXPIRY_IMMEDIATE,
    CMD_ALARM: EXPIRY_IMMEDIATE,
    CMD_SETPOINT: 0.1,
    CMD_LIMIT: 0.1,
    CMD_MODE: 1.0,
    CMD_TRACK: 1.0,
    CMD_IMON: EXPIRY_IMMEDIATE,
    CMD_PMON: EXPIRY_IMMEDIATE,
    CMD_ENABLE: 0.1,
    CMD_RPD: 1,
    CMD_CAL_ISCALE: 1,
}
OP_CODE_DICT_REV = {v: k for k, v in OP_CODE_DICT.iteritems()}

# ALARM FLAGS
NUM_ALARMS = 10
ALARM_OUT = 0x0000  # output status. 0: off, 1: on; equals XEN*LEN*REN
ALARM_XEN = 0x0001  # external enable flag, 0: J102 floating or HIGH, 1: LOW
ALARM_LEN = 0x0002  # local enable flag, 0: S100 enabled, 0: disabled
ALARM_REN = 0x0003  # remote enable flag, enable command state
ALARM_MODE1 = 0x0004  # feedback mode channel 1, 0: CC, 1: CP
ALARM_MODE2 = 0x0005  # feedback mode channel 2, 0: CC, 1: CP
ALARM_PARA = 0x0006  # parallel mode, state of track command, 0: independently
ALARM_IDENT = 0x0007  # status identify flag, 0: inactive, 1: active
ALARM_WRITE = 0x0008  # write to non-volatile memory in progress following SAVE
ALARM_CALMODE = 0x0009  # 1: device is in calibration mode, entered with PASSWD and left with REVERT
ALARM_FLAG_DICT = {
    'OUT':    ALARM_OUT,  # output status. 0: off, 1: on; equals XEN*LEN*REN
    'XEN':    ALARM_XEN,  # external enable flag, 0: J102 floating or HIGH, 1: LOW
    'LEN':    ALARM_LEN,  # local enable flag, 0: S100 enabled, 0: disabled
    'REN':    ALARM_REN,  # remote enable flag, enable command state
    'MODE1':  ALARM_MODE1,  # feedback mode channel 1, 0: CC, 1: CP
    'MODE2':  ALARM_MODE2,  # feedback mode channel 2, 0: CC, 1: CP
    'PARA':   ALARM_PARA,  # parallel mode, state of track command, 0: independently
    'IDENT':  ALARM_IDENT,  # status identify flag, 0: inactive, 1: active
    'WRITE':  ALARM_WRITE,  # write to non-volatile memory in progress following SAVE
    'CALMODE': ALARM_CALMODE,  # 1: device is in calibration mode, entered with PASSWD and left with REVERT
    }
ALARM_FLAG_DICT_REV = {v: k for k, v in ALARM_FLAG_DICT.iteritems()}

# FLAGS (instead of taking non-zero values as true, uses literal ASCII characters)
# I assume all input gets fed through atoi, sscan or similar?
FLAG_OFF = 0x0030  # ASCII 48, '0'
FLAG_ON = 0x0031  # ASCII 49, '1'

# end codes
ERR_OK = 0x0000  # no error
ERR_DEVTYPE = 0x0001  # device type field incorrect
ERR_CHANNEL = 0x0002  # channel number out of range
ERR_OPTYPE = 0x0003  # op_type not supported
ERR_NOTIMPL = 0x0004  # op_code not implemented
ERR_PENDING = 0x0005  # command received, but not completed [ignore data]
ERR_BUSY = 0x0006  # device currently busy, has not performed requested op
ERR_DATA = 0x0007  # data field content invalid for op_code
ERR_SAFETY = 0x0008  # requested op not within safety specs of config
ERR_CALMODE = 0x0009  # requested op only available in calibration mode!
END_CODE_DICT = {
    ERR_OK: "OK",
    ERR_DEVTYPE: "DEVTYPE",
    ERR_CHANNEL: "CHANNEL",
    ERR_OPTYPE: "OPTYPE",
    ERR_NOTIMPL: "NOTIMPL",
    ERR_PENDING: "PENDING",
    ERR_BUSY: "BUSY",
    ERR_DATA: "DATA",
    ERR_SAFETY: "SAFETY",
    ERR_CALMODE: "CALMODE"
}
END_CODE_DICT_REV = {v: k for k, v in END_CODE_DICT.iteritems()}
END_CODE_DESC_DICT = {
    ERR_OK: "No Error",
    ERR_DEVTYPE: "Incorrect device type",
    ERR_CHANNEL: "Channel number out of range",
    ERR_OPTYPE: "Op-type not supported",
    ERR_NOTIMPL: "Op-code not implemented",
    ERR_PENDING: "Pending, command received but data was ignored",
    ERR_BUSY: "Device busy, operation not performed",
    ERR_DATA: "Data field content invalid for op-code",
    ERR_SAFETY: "Requested operation not within safety specs",
    ERR_CALMODE: "Operation only available in calibration mode"
}

# DATA (data ignored for types read, min and max)
LEN_DATA = 16  # length data field in bytes

if __name__ == "__main__":
    from util import encode_command, decode_command
    print encode_command("")