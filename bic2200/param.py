MAX_RESEND = 5

MAX_VOUT_SET = 65
MIN_VOUT_SET = 38
MAX_REVERSE_VOUT_SET = 65
MIN_REVERSE_VOUT_SET = 38
MAX_IOUT_SET = 40
MIN_IOUT_SET = 9
MAX_REVERSE_IOUT_SET = 32.2
MIN_REVERSE_IOUT_SET = 9


TO_BIC = 0xC03
FROM_BIC = 0xC02

OPERATION = 0x00
VOUT_SET = 0x20
IOUT_SET = 0x30
FAULT_STATUS = 0x40
READ_VIN = 0x50
READ_VOUT = 0x60
READ_IOUT = 0x61
READ_TEMPERATURE = 0x62
MFR_ID1 = 0x80
MFR_ID2 = 0x81
MFR_ID = [MFR_ID1, MFR_ID2]
MFR_MODEL1 = 0x82
MFR_MODEL2 = 0x83
MFR_MODEL = [MFR_MODEL1, MFR_MODEL2]
MFR_REVISION = 0x84
MFR_LOCATION = 0x85
MFR_DATE = 0x86
MFR_SERIAL1 = 0x87
MFR_SERIAL2 = 0x88
MFR_SERIAL = [0x87, 0x88]
MFR_CMD = MFR_ID + MFR_MODEL + MFR_SERIAL + [
    MFR_REVISION,
    MFR_LOCATION,
    MFR_DATE
]
SCALING_FACTOR = 0xC0
SYSTEM_STATUS = 0XC1
SYSTEM_CONFIG = 0xC2
DIRECTION_CTRL = 0x100
REVERSE_VOUT_SET = 0x120
REVERSE_IOUT_SET = 0x130
BIDIRECTIONAL_CONFIG = 0x140