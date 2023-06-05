import unittest
from unittest.mock import MagicMock, patch

from bic2200 import *
from bic2200.canbus_recv import *

class TestBicCanListener(unittest.TestCase):
    @patch.object(BicCanListener, '__new__', lambda cls, *args, **kwargs: super(BicCanListener, cls).__new__(cls))
    def setUp(self):
        # Create a BicCanListener instance
        self.instance = BicCanListener()
        self.test_data = [0] * 8
    
    def test_on_message_received(self):
        msg = can.Message()
        msg.arbitration_id = 0xC0200
        msg.data = bytearray([0x20,0x00])
        self.instance._BicCanListener__assort_msg = MagicMock()
        self.instance.on_message_received(msg)
        self.instance._BicCanListener__assort_msg.assert_called_once()
    
    def test_on_message_received_for_rev(self):
        msg = can.Message()
        msg.arbitration_id = 0xC0200
        msg.data = bytearray([0x20, 0x01])
        self.instance._BicCanListener__assort_msg = MagicMock()
        self.instance.on_message_received(msg)
        self.instance._BicCanListener__assort_msg.assert_called_once()
    
    def test_on_message_received_cmd_unreconize(self):
        msg = can.Message()
        msg.arbitration_id = 0xC0200
        msg.data = bytearray([0x20,0x02])
        self.instance._BicCanListener__assort_msg = MagicMock()
        self.instance.on_message_received(msg)
        self.instance._BicCanListener__assort_msg.assert_not_called()
    
    def test_on_message_received_msgId_unreconize(self):
        msg = can.Message()
        msg.arbitration_id = 0xC0000
        msg.data = bytearray([0x20,0x00])
        self.instance._BicCanListener__assort_msg = MagicMock()
        self.instance.on_message_received(msg)
        self.instance._BicCanListener__assort_msg.assert_not_called()
    
    def test_assortMsg_operation(self):    
        # Replace the method with a MagicMock
        self.instance._BicCanListener__msg_set_operations = MagicMock()
        msgtype = 0

        # Call the assortMsg method
        self.instance._BicCanListener__assort_msg(msgtype)

        # Check if the  method was called
        self.instance._BicCanListener__msg_set_operations.assert_called_once()
    
    def test_assortMsg_unknown_input(self):
        
        # Replace the method with a MagicMock
        self.instance._BicCanListener__msg_set_operations = MagicMock()
        msgtype = 0xFF
        # Call the assortMsg method
        self.instance._BicCanListener__assort_msg(msgtype)

        # If an exception was raised, the test would fail
        self.assertTrue(True)
    
    def test_set2ByteMsgValue(self):
        self.test_data[2:3] = [0, 1]
        res = self.instance._convert_2bytes_msg_to_value(self.test_data)
        self.assertEqual(res, 256)
    
    def test_msgSetOperation(self):
        # Set up test data
        self.test_data[2:3] = [1, 0]
        self.instance._BicCanListener__msg_datas = self.test_data
        # Call the assortMsg method
        self.instance._BicCanListener__msg_set_operations()
        # Check if the operation value is correctly set
        self.assertEqual(self.instance._BicCanListener__operations, 0x01)
        self.assertEqual(self.instance.operations, 1)

    def test_extractAndSetFactor(self):
        self.test_data[3] = 0x50
        self.instance._BicCanListener__msg_datas = self.test_data
        factorIndex = 3
        shiftBits = 4
        result = self.instance._BicCanListener__extract_and_set_factor(factorIndex, shiftBits)
        self.assertEqual(result, -2)
    
    def test_extractAndSetFactor_0(self):
        self.test_data[4] = 0x02
        self.instance._BicCanListener__msg_datas = self.test_data
        factorIndex = 4
        shiftBits = 0
        result = self.instance._BicCanListener__extract_and_set_factor(factorIndex, shiftBits)
        self.assertEqual(result, 0)
    
    def test_msgSetScalingFactor(self):
        self.test_data[2:6] = [0x55, 0xA3, 0x09, 0x04]
        self.instance._BicCanListener__msg_datas = self.test_data
        self.instance._BicCanListener__msg_set_scaling_factor()
        self.assertEqual(self.instance._BicCanListener__vout_factor, -2)
        self.assertEqual(self.instance._BicCanListener__iout_factor, -2)
        self.assertEqual(self.instance._BicCanListener__vin_factor, 0)
        self.assertEqual(self.instance._BicCanListener__fan_speed_factor, 0)
        self.assertEqual(self.instance._BicCanListener__temperature_factor, 2)
        self.assertEqual(self.instance._BicCanListener__iin_factor, -3)
        
        self.assertEqual(self.instance.vout_factor, -2)
        self.assertEqual(self.instance.iout_factor, -2)
        self.assertEqual(self.instance.vin_factor, 0)
        self.assertEqual(self.instance.fan_speed_factor, 0)
        self.assertEqual(self.instance.temperature_factor, 2)
        self.assertEqual(self.instance.iin_factor, -3)
    
    def test_msgSetSystemConfig(self):
        self.test_data[2] = 0x01
        self.instance._BicCanListener__msg_datas = self.test_data
        self.instance._BicCanListener__msg_set_system_configs()
        self.assertEqual(self.instance._BicCanListener__sys_configs, ["CAN_CRTL", "DEFAULT_OFF"])
        self.assertEqual(self.instance.sys_configs, ["CAN_CRTL", "DEFAULT_OFF"])
    
    def test_msgSetSystemConfig_unknown_input(self):
        self.test_data[2] = 0x06
        self.instance._BicCanListener__msg_datas = self.test_data
        self.instance._BicCanListener__msg_set_system_configs()
        self.assertEqual(self.instance._BicCanListener__sys_configs, ["SVR"])
        self.assertEqual(self.instance.sys_configs, ["SVR"])
    
    def test_msgSetSystemStatus_allon(self):
        self.test_data[2:3]=[0xFF, 0x00]
        self.instance._BicCanListener__msg_datas = self.test_data
        self.instance._BicCanListener__msg_set_system_status()
        self.assertEqual(self.instance._BicCanListener__sys_status, ["MASTER", "DC_OK", "PFC_OK", "ADL_ON","INITIAL_STATE"])
        self.assertEqual(self.instance.sys_status, ["MASTER", "DC_OK", "PFC_OK", "ADL_ON","INITIAL_STATE"])
    
    def test_msgSetSystemStatus_alloff(self):
        self.test_data[2:3]=[0x00, 0xFF]
        self.instance._BicCanListener__msg_datas = self.test_data
        self.instance._BicCanListener__msg_set_system_status()
        self.assertEqual(self.instance._BicCanListener__sys_status, ["SLAVE", "EEPEROM_OK"])
        self.assertEqual(self.instance.sys_status, ["SLAVE", "EEPEROM_OK"])
    
    def test_msgSetMfrId1(self):
        self.test_data[2:] = list(bytearray("MEAN", "ascii"))
        self.instance._BicCanListener__msg_datas = self.test_data
        self.instance._BicCanListener__msg_set_mfr_id1()
        self.assertEqual(self.instance._BicCanListener__mfr_id1, "MEAN")
     
    def test_msgSetMfrRev(self):
        self.test_data[2:] = [12, 12, 0xFF, 0xFF, 0xFF, 0xFF]
        self.instance._BicCanListener__msg_datas = self.test_data
        self.instance._BicCanListener__msg_set_mfr_rev()
        self.assertEqual(self.instance._BicCanListener__mfr_rev, ["Rev1.2", "Rev1.2"])
     
if __name__ == '__main__':
    unittest.main()
