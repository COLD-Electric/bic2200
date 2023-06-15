from bic2200.canbus_send import BicCanSend, SendListener
from bic2200.canbus_recv import BicCanListener
from bic2200 import *
import logging
import time
import can

class Bic2200(object):
    def __init__(self, canbus: can.Bus, bic_device_number=0):
        self.canbus = canbus
        self.listener = BicCanListener()
        self.bic_device_number = bic_device_number
        # Create a BmsCanListener object to listen to the CAN bus
        self.poster = BicCanSend(self.canbus)
        self.post_checker = SendListener()
    
    def __repr__(self) -> str:
       return str(self.listener.mfr_details)
    
    def __str__(self) -> str:
        mfr = self.listener.mfr_details
        string = ""
        for s in mfr.keys():
            string = string + f"{s}:\t{str(mfr[s])}\n"
        return string
        
    def get_voltage_and_current(self) -> list[int]:
        """
        Get the voltage and current of the BIC2200.

        Returns:
            list[int]: A list containing the voltage and current values.
        """
        vout = self.listener.vout_read
        iout = self.listener.iout_read
        return [vout, iout]
    
    def boot(self) -> SendListener:
        """
        Boot up the BIC2200.

        Returns:
            SendListener: A SendListener object.
        """
        # Create a thread to send messages
        send_msg_task = threading.Thread(target=self.poster.read, args=(self.post_checker, self.bic_device_number))
        send_msg_task.start()
        
        # Add the listener to the CAN bus
        can.Notifier(self.canbus, [self.listener, self.post_checker])
        return self.listener
    @property
    def _new_send_msg_params(self):
        return{
            "operation": self.listener.operations,
            "direct_control": self.listener.dir_ctrl,
            "vout_set": self.listener.vout_set,
            "reverse_vout_set": self.listener.rev_vout_set,
            "iout_set": self.listener.iout_set,
            "reverse_iout_set": self.listener.rev_iout_set,
        }
    @property
    def factors(self):
        return {
            "vout_set": self.listener.vout_factor,
            "reverse_vout_set": self.listener.rev_vout_factor,
            "iout_set": self.listener.iout_factor,
            "reverse_iout_set": self.listener.rev_iout_set,
        }
    def _send_msg(self, str_param, value) -> None:
        """
        Send a message to the BIC2200.

        Args:
            str_param (str): The parameter to set.
            value (float): The value to set the parameter to.
        """
        read_param = self._new_send_msg_params[str_param]
        logging.debug(f"WRITE\tparam:{str_param}\tset_value:{value}\tread_value:{read_param}")
        if read_param is None:
            raise KeyError(f"param{str_param} not in list")
        resend_times = 0
        while read_param != value:
            self.poster.write(str_param, value, self.bic_device_number)
            resend_times = resend_times + 1
            time.sleep(2)
            read_param = self._new_send_msg_params[str_param]
            logging.debug(f"READ{resend_times}\tparam:{str_param}\tset_value:{value}\tread_value:{read_param}")
            if resend_times > MAX_RESEND - 1:
                raise RuntimeError(f"No response received for message {str_param}")

    def _set_param(self, param: str, value: float) -> None:
        """
        Sends a message to set a parameter.
    
        Args:
            param (str): The parameter to set.
            value (float): The value to set the parameter to.
        """
        try:
            max_val = globals()[f"MAX_{param.upper()}_SET"]
            min_val = globals()[f"MIN_{param.upper()}_SET"]
        except KeyError:
            raise KeyError(f"param '{param}' not in list")
        try:
            param = param + "_set"
            factor = self.factors[param]
        except KeyError:
            raise KeyError(f"factor '{param}' not found")
        
        if value > max_val:
            value = max_val
        elif value < min_val:
            value = min_val
        else:
            factor = self.factors[param]
            value = round(value / factor)
        self._send_msg(param, value)
    
    def start(self) -> None:
        """
        Sends a message to start the BIC device.
        """
        self._send_msg("operation", 1)
    
    def stop(self) -> None:
        """
        Sends a message to stop the BIC device.
        """
        self._send_msg("operation", 0)
    
    def charge(self) -> None:
        """
        Sends a message to set the BIC device to charge mode.
        """
        self._send_msg("direct_control", 0)
    
    def discharge(self) -> None:
        """
        Sends a message to set the BIC device to discharge mode.
        """
        self._send_msg("direct_control", 1)
        
    def set_vout(self, vout: float) -> None:
        """
        Sends a message to set the output voltage.
    
        Args:
            vout (float): The value to set the output voltage to.
        """
        self._set_param("vout", vout)
        
    def set_rev_vout(self, rev_vout_set: float) -> None:
        """
        Sends a message to set the reverse output voltage.
    
        Args:
            rev_vout_set (float): The value to set the reverse output voltage to.
        """
        self._set_param("reverse_vout", rev_vout_set)
    
    def set_iout(self, iout: float) -> None:
        """
        Sends a message to set the output current.
    
        Args:
            iout (float): The value to set the output current to.
        """
        self._set_param("iout", iout)
    
    def set_rev_iout(self, rev_iout_set: float) -> None:
        """
        Sends a message to set the reverse output current.
    
        Args:
            rev_iout_set (float): The value to set the reverse output current to.
        """
        self._set_param("reverse_iout", rev_iout_set)

    def get_voltage_and_current(self) -> list[int]:
        """
        Returns a list containing the voltage and current readings.
    
        Returns:
            list[int]: A list containing the voltage and current readings.
        """
        vout = self.listener.vout_read
        iout = self.listener.iout_read
        return [vout, iout]
    
    def set_can_ctrl(self) -> None:
        """
        Sends messages to set the CAN bus control.
        """
        sys = self.listener.sys_configs
        while (sys & 0x01) != 1:
            self.poster.write("system_config", (sys | 0x01), self.bic_device_number)
            sys = self.listener.sys_configs
        while (self.listener.bidir_configs & 0x01) != 1:
            self.poster.write("bidirectional_config", 0x01, self.bic_device_number)
    
    def set_auto_ctrl(self) -> None:
        """
        Sends messages to set the automatic control.
        """
        while (self.listener.bidir_configs & 0x01) != 0:
            self.poster.write("bidirectional_config", 0x00, self.bic_device_number)
        sys = self.listener.sys_configs
        while (sys & 0x01) != 0:
            self.poster.write("system_config", (sys & 0x06), self.bic_device_number)
            sys = self.listener.sys_configs
    
    def set_operation_init(self, switch) -> None:
        """
        Sends a message to initialize the operation.
    
        Args:
            switch (int): The value to set the operation to.
        """
        if switch > 1:
            switch = 2
        sys = self.listener.sys_configs
        while(sys >> 1) != switch:
            self.poster.write("system_config", (switch << 1) | (sys & 0x01), self.bic_device_number)
            sys = self.listener.sys_configs
