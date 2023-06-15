from bic2200 import *
import logging
       
class SendListener(can.Listener):
    instance = None
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance
    
    def __init__(self):
        self.__received_flag = False
    
    def on_message_received(self, msg):
        """
        Receives and parses CAN messages.

        Args:
            msg (can.Message): The received CAN message.
        """
        self.__received_flag = True
    
    def reset_received_flag(self):
        """
        Resets the receive check flag to False.
        """
        self.__received_flag = False
    @property
    def received_flag(self):
        """
        Returns the receive check flag.

        Returns:
            bool: The receive check flag.
        """
        return self.__received_flag

class BicCanSend(object):
    instance = None
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance
    
    def __init__(self, canbus: can.Bus):
        self.canbus = canbus
    
    def _send_msg(self, listener: SendListener, bic_device_number: int, send_address_list: list[int]):
        """
        Send messages over the CAN bus and wait for a response before moving to the next message in the list.

        Args:
            listener (Listener): An instance of the `Listener` class used to check for incoming messages on the CAN bus.
            bic_device_number (int): An integer representing the number of the BIC device.
            sendList (list): A list of message IDs to be sent over the CAN bus.

        Raises:
            RuntimeError: If no response is received after the maximum number of resend attempts.

        Returns:
            None
        """
        for send_address in send_address_list:
            # Construct the message ID using the TO_BIC constant, bicDevNo, and the current message ID being sent
            dlc = 2
            msg_id = (TO_BIC << 8) + bic_device_number
            msg_datas = [(send_address & 0x0FF), ((send_address >> 8) & 0x0FF)]
            # Set the message data to a fixed msgData array and the is_extended_id flag to True
            msg = can.Message(arbitration_id=msg_id, data=bytearray(msg_datas), dlc=dlc, is_extended_id=True)
            
            resend_times = 0
            while not listener.received_flag and resend_times < MAX_RESEND:
                # Resend the message if no response is received after a certain amount of time
                self.canbus.send(msg)
                resend_times += 1
                time.sleep(0.5)
            if not listener.received_flag:
                # If no response is received after the maximum number of resend attempts, raise an error
                raise RuntimeError("No response received for message ID: 0x{:02x}".format(send_address))
            else:
                # Reset the receive check flag after a response is received
                listener.reset_received_flag()
        
    def read(self, listener, bic_device_number):
        """
        Send messages over the CAN bus in a loop to request cell voltages, temperature, and system messages.

        Args:
            listener (Listener): An instance of the `Listener` class used to check for incoming messages on the CAN bus.
            bicDevNo (int): An integer representing the number of the BIC device.

        Returns:
            None
        """
        # Create a list of message IDs to be sent during initialization
        init_send_ids_list = MFR_CMD + [
            SCALING_FACTOR,
        ]
        # Create a list of message IDs to be sent in a loop
        loop_send_id_list = [
            OPERATION,
            VOUT_SET,
            IOUT_SET,
            FAULT_STATUS,
            READ_VIN,
            READ_VOUT,
            READ_IOUT,
            READ_TEMPERATURE,
            SYSTEM_STATUS,
            SYSTEM_CONFIG,
            DIRECTION_CTRL,
            REVERSE_VOUT_SET,
            REVERSE_IOUT_SET,
            BIDIRECTIONAL_CONFIG,
        ]
        # Send the initialization messages first
        self._send_msg(listener, bic_device_number, init_send_ids_list)
        # Enter an infinite loop and send messages to each of the message IDs in the loopSendIdList
        while True:
            self._send_msg(listener, bic_device_number, loop_send_id_list)
    
    def write(self, str_param, write_datas, bic_device):
        params_list = {
            "vout_set" : [VOUT_SET, 2],
            "iout_set" : [IOUT_SET, 2],
            "reverse_vout_set" : [REVERSE_VOUT_SET, 2],
            "reverse_iout_set" : [REVERSE_IOUT_SET, 2],          
            "operation" : [OPERATION, 1],
            "direct_control" : [DIRECTION_CTRL, 1],
            
            "bidirectional_config" : [BIDIRECTIONAL_CONFIG, 2],
            "system_config" : [SYSTEM_CONFIG, 2],
        }
        
        param = params_list.get(str_param)
        if param is not None:
            msgId = (TO_BIC << 8) + bic_device
            msg_datas = [(param[0] & 0x0FF), ((param[0] >> 8) & 0x0FF)]
            for i in range(param[1]):
                msg_datas.append((write_datas >> (8 * i)) & 0x0FF)
            dlc = param[1] + 2
            msg = can.Message(arbitration_id=msgId, data=bytearray(msg_datas), dlc=dlc, is_extended_id=True)
            self.canbus.send(msg)
            
            