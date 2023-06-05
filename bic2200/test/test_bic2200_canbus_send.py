import unittest
from unittest.mock import MagicMock, patch

from bic2200 import *
from bic2200.canbus_send import *

class StubClass:
    pass

class TestRuntimeError(Exception):
    pass

def stub_method(*args, **kwargs):
    pass

class TestBicSendListener(unittest.TestCase):
    @patch.object(SendListener, '__new__', lambda cls, *args, **kwargs: super(SendListener, cls).__new__(cls))
    def setUp(self):
        self.instance = SendListener()
    
    def test_on_message_received(self):
        msg = can.Message()
        self.instance.on_message_received(msg)
        result1 = self.instance._SendListener__received_flag
        result2 = self.instance.received_flag
        self.assertEqual(result1, True)
        self.assertEqual(result2, True)

    def test_reset_recv_flag(self):
        self.instance._SendListener__received_flag = True
        self.instance.reset_received_flag()
        result1 = self.instance._SendListener__received_flag
        result2 = self.instance.received_flag
        self.assertEqual(result1, False)
        self.assertEqual(result2, False)

class TestBicCanSend(unittest.TestCase):
    @patch.object(BicCanSend, '__new__', lambda cls, *args, **kwargs: super(BicCanSend, cls).__new__(cls))
    @patch.object(SendListener, '__new__', lambda cls, *args, **kwargs: super(SendListener, cls).__new__(cls))
    def setUp(self):
        self.canbus = StubClass()
        self.listener = SendListener()
        self.instance = BicCanSend(self.canbus)
    
    @patch.object(SendListener, 'received_flag', False)
    def test_send_msg(self):
        self.canbus.send = MagicMock(side_effect=[TestRuntimeError()])
        try:
            self.instance._send_msg(self.listener, 1, [0])
        except TestRuntimeError:
            pass
        self.canbus.send.assert_called_once()

    @patch.object(SendListener, 'received_flag', False)
    @patch("time.sleep", stub_method)
    def test_send_msg_runtime_error(self):
        self.canbus.send = MagicMock()
        with self.assertRaises(RuntimeError):
            self.instance._send_msg(self.listener, 1, [0])
        self.assertEqual(self.canbus.send.call_count, MAX_RESEND)
    
    @patch.object(SendListener, 'received_flag', True)
    def test_send_msg_received_true(self):
        self.canbus.send = MagicMock()
        self.listener.reset_received_flag = MagicMock()
        self.instance._send_msg(self.listener, 1, [0])
        self.canbus.send.assert_not_called()
        self.listener.reset_received_flag.assert_called_once()
    
    def test_read(self):
        self.instance._send_msg = MagicMock(side_effect=[None, None, TestRuntimeError()])
        try:
            self.instance.read(self.listener, 1)
        except TestRuntimeError:
            pass
        self.assertEqual(self.instance._send_msg.call_count, 3)
    
    def test_write(self):
        self.canbus.send = MagicMock()
        self.instance.write("operation", 1, 1)
        self.canbus.send.assert_called_once()
    
    def test_write_param_none(self):
        self.canbus.send = MagicMock()
        self.instance.write("none", 1, 1)
        self.canbus.send.assert_not_called()
    
if __name__ == '__main__':
    unittest.main()
    