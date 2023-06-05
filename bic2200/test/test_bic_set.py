import unittest
from unittest.mock import MagicMock, patch

from bic2200 import *
from bic2200.bic_set import Bic2200

class StubClass:
    pass

class TestRuntimeError(Exception):
    pass

def stub_method(*args, **kwargs):
    pass

class TestBIC2200(unittest.TestCase):
    def setUp(self):
        self.canbus = StubClass()
        self.instance = Bic2200(self.canbus)
    
    def test_send_msg(self):
        self.instance.poster.write = MagicMock(side_effect=[TestRuntimeError])
        try:
            self.instance._send_msg("operation", 1)
        except:
            pass
        self.instance.poster.write.assert_called_once()
    
    def test_send_msg_value_not_change(self):
        self.instance.poster.write = MagicMock()
        self.instance._send_msg("operation", 0)
        self.instance.poster.write.assert_not_called()
    
    @patch("time.sleep", stub_method)
    def test_send_msg_runtime(self):
        self.instance.poster.write = MagicMock()
        with self.assertRaises(RuntimeError):
            self.instance._send_msg("operation", 1)
        self.assertEqual(self.instance.poster.write.call_count, MAX_RESEND)
    
    def test_send_msg_param_fault(self):
        self.instance.poster.write = MagicMock()
        with self.assertRaises(KeyError):
            self.instance._send_msg("0", 0)
        self.instance.poster.write.assert_not_called()
    
    def test_set_param(self):
        self.instance._send_msg = MagicMock()
        self.instance._set_param("iout", 20)
        self.instance._send_msg.assert_called_with("iout_set", 20)
    
    def test_set_param_max(self):
        self.instance._send_msg = MagicMock()
        self.instance._set_param("vout", MAX_VOUT_SET + 1)
        self.instance._send_msg.assert_called_with("vout_set", MAX_VOUT_SET)
    
    def test_set_param_min(self):
        self.instance._send_msg = MagicMock()
        self.instance._set_param("reverse_vout", MIN_REVERSE_VOUT_SET - 1)
        self.instance._send_msg.assert_called_with("reverse_vout_set", MIN_REVERSE_VOUT_SET)
    
    def test_set_param_fault(self):
        self.instance._send_msg = MagicMock()
        with self.assertRaises(KeyError):
            self.instance._set_param("0", 0)
        self.instance._send_msg.assert_not_called()

if __name__ == '__main__':
    unittest.main()
    