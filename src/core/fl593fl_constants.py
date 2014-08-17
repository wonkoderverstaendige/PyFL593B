# -*- coding: utf-8 -*-
"""
Created on 08 Apr 2014 1:48 PM
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

Constants used by the FL593FL device class.
"""

# DEVICE BEHAVIOR
TIMEOUT = 100  # default timeout of read/write is 1000 ms

AUTO_START_ZERO_SET = True  # For safety reasons, try to disable
AUTO_START_ZERO_LIMIT = True  # For safety reasons, try to zero
START_REMOTE_ENABLE_STATE = False  # Set to state on startup

AUTO_EXIT_ZERO_SET = True  # For safety reasons, try to disable
AUTO_EXIT_ZERO_LIMIT = True  # For safety reasons, try to zero
EXIT_REMOTE_ENABLE_STATE = False  # For safety reasons, disable on exit

# DEVICE CONSTANTS
VENDOR_ID = 0x1a45
PRODUCT_ID = 0x2001
DEVICE_TYPE = 0x0
CONFIGURATION = 1
MAX_CONN_RETRIES = 10
EP_ADDR_OUT = 0x01
EP_PACK_OUT = 20  # length bytes to send
EP_ADDR_IN = 0x82
EP_PACK_IN = 21  # length bytes returned

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
ERROR_DICT = {
    ERR_OK: "OK",
    ERR_DEVTYPE: "Incorrect device type",
    ERR_CHANNEL: "Channel number out of range",
    ERR_OPTYPE: "Op-type not supported",
    ERR_NOTIMPL: "Op-code not implemented",
    ERR_PENDING: "Pending, command received but data was ignored",
    ERR_BUSY: "Device busy, operation not performed",
    ERR_DATA: "Data field content invalid for op_code",
    ERR_SAFETY: "Requested operation not within safety specs",
    ERR_CALMODE: "Operation only available in calibration mode"}

# Channels
MAX_NUM_CHAN = 2  # (0: device, 1: channel 1, 2: channel 2)
CHAN_STATUS = 0x0
CHAN_LD1 = 0x1
CHAN_LD2 = 0x2

# OpTypes
TYPE_READ = 0x01  # return OpCode quantity to host
TYPE_WRITE = 0x02  # write OpCode  quantity to device
TYPE_MIN = 0x03  # return minimum of OpCode quantity to host
TYPE_MAX = 0x04  # return maximum of OpCode quantity to host
OP_TYPE_DICT = {
    TYPE_READ: "READ",
    TYPE_WRITE: "WRITE",
    TYPE_MIN: "MIN",
    TYPE_MAX: "MAX"
}
OP_TYPE_DICT_REV = {v: k for v, k in OP_TYPE_DICT.iteritems()}

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
CMD_TRACK = 0x14  # rw, tracking configuration (independent: 0/parallel: 1)
CMD_IMON = 0x15  # current monitor
CMD_PMON = 0x16  # power monitor
CMD_ENABLE = 0x17  # rw, output enable. Additionally requires the output enable switch
# on the board to be set to EN, and the NT pin to be pulled LOW
CMD_RPD = 0x19  # rwm, kOhm, photodiode feedback resistor for specified channel
CMD_CAL_ISCALE = 0xE2  # rw, current monitor calibration scaling value for selected channel


# ALARM FLAGS
NUM_ALARMS = 10
ALARM_OUT = 0x00  # output status. 0: off, 1: on; equals XEN*LEN*REN
ALARM_XEN = 0x01  # external enable flag, 0: J102 floating or HIGH, 1: LOW
ALARM_LEN = 0x02  # local enable flag, 0: S100 enabled, 0: disabled
ALARM_REN = 0x03  # remote enable flag, enable command state
ALARM_MODE1 = 0x04  # feedback mode channel 1, 0: CC, 1: CP
ALARM_MODE2 = 0x05  # feedback mode channel 2, 0: CC, 1: CP
ALARM_PARA = 0x06  # parallel mode, state of track command, 0: independently
ALARM_IDENT = 0x07  # status identify flag, 0: inactive, 1: active
ALARM_WRITE = 0x08  # write to non-volatile memory in progress following SAVE
ALARM_CALMODE = 0x09  # 1: device is in calibration mode, entered with PASSWD and left with REVERT
ALARM_FLAG_DICT = {
    ALARM_OUT: 'OUT',
    ALARM_XEN: 'XEN',
    ALARM_LEN: 'LEN',
    ALARM_REN: 'REN',
    ALARM_MODE1: 'MODE1',
    ALARM_MODE2: 'MODE2',
    ALARM_PARA: 'PARA',
    ALARM_IDENT: 'IDENT',
    ALARM_WRITE: 'WRITE',
    ALARM_CALMODE: 'CALMODE'}
ALARM_FLAG_DICT_REV = {v: k for v, k in ALARM_FLAG_DICT.iteritems()}

# DATA (data ignored for types read, min and max)
LEN_DATA = 16  # length data field in bytes

# FLAGS (instead of taking non-zero values as true, uses literal ASCII characters)
# I assume all input gets fed through atoi, sscan or similar?
FLAG_OFF = 0x30  # ASCII 48, '0'
FLAG_ON = 0x31  # ASCII 49, '1'
