import can

MAX_RESEND = 5

RECV_CELL_VOLTAGE_START = 0x04
RECV_CELL_VOLTAGE_END = 0x6B
RECV_CELL_VOLTAGE = range(RECV_CELL_VOLTAGE_START, RECV_CELL_VOLTAGE_END)
RECV_TEMP_START = 0x6C
RECV_TEMP_END = 0x78
RECV_TEMP = range(RECV_TEMP_START, RECV_TEMP_END)
RECV_MSG1 = 0x01
RECV_MSG2 = 0x02
RECV_MSG3 = 0x03
RECV_ID_CMD = 0x0A

SEND_CELL_VOLTAGE_START = 0x02
SEND_CELL_VOLTAGE_END = 0x04
SEND_CELL_VOLTAGE = range(SEND_CELL_VOLTAGE_START, SEND_CELL_VOLTAGE_END)
SEND_TEMP = 0x05
SEND_SYS_MSG = 0x01
SEND_ID_CMD = 0x0F
SEND_DATA_CMD = [1, 0, 0, 0, 0, 0, 0, 0]

RELAY_CTRL = 0x0101
CLEAR_PF = 0x0102
FAN_CTRL = 0x0103
CONTROL_ID_CMD = 0x01