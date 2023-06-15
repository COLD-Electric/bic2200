from datetime import datetime
from bic2200 import *
import logging
import can

class BicCanListener(can.Listener):
    def __init__(self):
        """
        Initializes a BicCanListener object with a list of desired CAN message IDs to receive and
        variables to store the received data.
        """
        # Variables to store received data
        self.__mfr_id1 = ""
        self.__mfr_id2 = ""
        self.__mfr_model1 = ""
        self.__mfr_model2 = ""
        self.__mfr_date = ""
        self.__mfr_serial = 0
        self.__mfr_rev = []
        self.__fault_status = []
        self.__sys_status = []
        self.__sys_configs = []
        self.__bidir_configs = []
        self.__msg_datas = []
        self.__operations = 0
        self.__rev_iout_factor = 0
        self.__temperature_factor = 0
        self.__fan_speed_factor = 0
        self.__rev_vout_factor = 0
        self.__iout_factor = 0
        self.__vout_factor = 0
        self.__set_vout = 0
        self.__set_iout = 0
        self.__set_rever_vout = 0
        self.__set_rever_iout = 0
        self.__read_vin = 0
        self.__read_vout = 0
        self.__read_iout = 0
        self.__read_temperature = 0
        self.__dir_ctrl = 0
    
    # Getters for private variables
    @property
    def mfr_details(self):
        if self.__mfr_id1 != "" and self.__mfr_id2 != "":
            mfrId = self.__mfr_id1 + self.__mfr_id2
        else:
            mfrId = ""
        if self.__mfr_model1 != "" and self.__mfr_model2 != "":
            mfr_model = self.__mfr_model1 + self.__mfr_model2
        else:
            mfr_model = ""
        
        mfr_contents = {
            "mfr_name" : mfrId,
            "mfr_date" : self.__mfr_date,
            "machine_type": mfr_model,
            "machine_serial": self.__mfr_serial,
            "mcu_rev": self.__mfr_rev,
        }
        return mfr_contents
    
    @property
    def fault_status(self):
        """
        Returns the list of fault status values.

        Returns:
            list: A list of fault status values.
        """
        return self.__fault_status
    @property
    def sys_status(self):
        """
        Returns the list of system status values.

        Returns:
            list: A list of system status values.
        """
        return self.__sys_status
    @property
    def sys_configs(self):
        """
        Returns the list of system configuration values.

        Returns:
            list: A list of system configuration values.
        """
        return self.__sys_configs
    @property
    def bidir_configs(self):
        """
        Returns the list of bidirectional configuration values.

        Returns:
            list: A list of bidirectional configuration values.
        """
        return self.__bidir_configs
    @property
    def operations(self):
        """
        Returns the value of the operation.

        Returns:
            int: The value of the operation.
        """
        return self.__operations
    @property
    def rev_iout_factor(self):
        """
        Returns the value of the reverse Iout factor.

        Returns:
            int: The value of the reverse Iout factor.
        """
        return self.__rev_iout_factor
    @property
    def temperature_factor(self):
        """
        Returns the value of the temperature factor.

        Returns:
            int: The value of the temperature factor.
        """
        return self.__temperature_factor
    @property
    def fan_speed_factor(self):
        """
        Returns the value of the fan speed factor.

        Returns:
            int: The value of the fan speed factor.
        """
        return self.__fan_speed_factor
    @property
    def rev_vout_factor(self):
        """
        Returns the value of the reverse Vout factor.

        Returns:
            int: The value of the reverse Vout factor.
        """
        return self.__rev_vout_factor
    @property
    def iout_factor(self):
        """
        Returns the value of the Iout factor.

        Returns:
            int: The value of the Iout factor.
        """
        return self.__iout_factor
    @property
    def vout_factor(self):
        """
        Returns the value of the Vout factor.

        Returns:
            int: The value of the Vout factor.
        """
        return self.__vout_factor
    @property
    def vout_set(self):
        """
        Returns the value of the set Vout.

        Returns:
            int: The value of the set Vout.
        """
        return self.__set_vout
    @property
    def iout_set(self):
        """
        Returns the value of the set Iout.

        Returns:
            int: The value of the set Iout.
        """
        return self.__set_iout
    @property
    def rev_vout_set(self):
        """
        Returns the value of the set reverse Vout.

        Returns:
            int: The value of the set Vout.
        """
        return self.__set_rever_vout
    @property
    def rev_iout_set(self):
        """
        Returns the value of the set reverse Iout.

        Returns:
            int: The value of the set Vout.
        """
        return self.__set_rever_iout
    @property
    def vin_read(self):
        """
        Returns the value of the read Vin.

        Returns:
            int: The value of the read Vin.
        """
        return round(self.__read_vin * (10 ** self.__rev_vout_factor), 2)
    @property
    def vout_read(self):
        """
        Returns the value of the read Vout.

        Returns:
            int: The value of the read Vout.
        """
        return round(self.__read_vout * (10 ** self.__vout_factor), 2)
    @property
    def iout_read(self):
        """
        Returns the value of the read Iout.

        Returns:
            int: The value of the read Iout.
        """
        if (self.__read_iout >> 15) & 0x01 == 1:
            self.__read_iout = -((~self.__read_iout & 0x0FFFF)+1)
        return round(self.__read_iout * (10 ** self.__iout_factor), 2)
    @property
    def temperature_read(self):
        """
        Returns the value of the read temperature.

        Returns:
            int: The value of the read temperature.
        """
        return round(self.__read_temperature * (10 ** self.__temperature_factor), 2)
    @property
    def dir_ctrl(self):
        """
        Returns the value of the direction control.

        Returns:
            int: The value of the direction control.
        """
        return self.__dir_ctrl
    
    def on_message_received(self, msg):
        """
        Receives and parses CAN messages that match the desired IDs.

        Args:
            msg (can.Message): The received CAN message.
        """
        cmds_list = MFR_CMD + [
            # MFR_CMD is a predefined list of CAN message IDs
            # Other custom CAN message IDs are also included
            OPERATION,
            VOUT_SET,
            IOUT_SET,
            FAULT_STATUS,
            READ_VIN,
            READ_VOUT,
            READ_IOUT,
            READ_TEMPERATURE,
            SCALING_FACTOR,
            SYSTEM_STATUS,
            SYSTEM_CONFIG,
            DIRECTION_CTRL,
            REVERSE_VOUT_SET,
            REVERSE_IOUT_SET,
            BIDIRECTIONAL_CONFIG,
        ]
        bic_device = msg.arbitration_id & 0x0FF
        recieved_flag = (msg.arbitration_id >> 8) & 0x0FFF
        cmd = (list(msg.data)[1] << 8) + list(msg.data)[0]
        if recieved_flag == FROM_BIC and cmd in cmds_list:
            self.__msgId = msg.arbitration_id
            self.__msg_datas = list(msg.data)
            self.__msgDlc = msg.dlc
            self.__assort_msg(cmd)

    def __assort_msg(self, msg_type):
        """
        Determines the message type based on the high byte of the message ID and calls the
        appropriate method to parse the message data.
        """
        # Call the appropriate method to parse the message data based on its type
        msg_handlers = {
            MFR_ID1: self.__msg_set_mfr_id1,
            MFR_ID2: self.__msg_set_mfr_id2,
            MFR_MODEL1: self.__msg_set_mfr_model1,
            MFR_MODEL2: self.__msg_set_mfr_model2,
            MFR_REVISION: self.__msg_set_mfr_rev,
            MFR_DATE: self.__msg_set_mfr_date,
            MFR_SERIAL2: self.__msg_set_mfr_serial,
            OPERATION: self.__msg_set_operations,
            VOUT_SET: self.__msg_set_vout_set,
            IOUT_SET: self.__msg_set_iout_set,
            FAULT_STATUS: self.__msg_set_fault_status,
            READ_VIN: self.__msg_set_read_vin,
            READ_VOUT: self.__msg_set_read_vout,
            READ_IOUT: self.__msg_set_read_iout,
            READ_TEMPERATURE: self.__msg_set_read_temperature,
            SCALING_FACTOR: self.__msg_set_scaling_factor,
            SYSTEM_STATUS: self.__msg_set_system_status,
            SYSTEM_CONFIG: self.__msg_set_system_configs,
            DIRECTION_CTRL: self.__msg_set_dirction_control,
            REVERSE_VOUT_SET: self.__msg_set_rever_set_vout,
            REVERSE_IOUT_SET: self.__msg_set_rever_set_iout,
            BIDIRECTIONAL_CONFIG: self.__msg_set_bidirectional_configs,
            }

        handler = msg_handlers.get(msg_type)
        if handler:
            handler()
    @staticmethod
    def _convert_2bytes_msg_to_value(msg_datas):
        """
        Convert a 2-byte message value from a received message.
        
        Returns:
            int: The converted 2-byte message value.
        """
        return (msg_datas[3] << 8) + msg_datas[2]
    
    # Private methods to process received messages
    def __msg_set_operations(self):
        """
        Sets the value of the operation parameter from a received message.
        """
        self.__operations = self.__msg_datas[2]
    
    def __msg_set_dirction_control(self):
        """
        Sets the direction control from a received message.
        """
        self.__dir_ctrl = self.__msg_datas[2]
    
    def __msg_set_vout_set(self):
        """
        Sets the value of the set Vout parameter from a received message.
        """
        self.__set_vout = self._convert_2bytes_msg_to_value(self.__msg_datas)
        
    def __msg_set_iout_set(self):
        """
        Sets the value of the set Iout parameter from a received message.
        """
        self.__set_iout = self._convert_2bytes_msg_to_value(self.__msg_datas)
    
    def __msg_set_read_vin(self):
        """
        Sets the value of the read Vin parameter from a received message.
        """
        self.__read_vin = self._convert_2bytes_msg_to_value(self.__msg_datas)
        
    def __msg_set_read_vout(self):
        """
        Sets the value of the read Vout parameter from a received message.
        """
        self.__read_vout = self._convert_2bytes_msg_to_value(self.__msg_datas)
        
    def __msg_set_read_iout(self):
        """
        Sets the value of the read Iout parameter from a received message.
        """
        self.__read_iout = self._convert_2bytes_msg_to_value(self.__msg_datas)
        
    def __msg_set_read_temperature(self):
        """
        Sets the value of the read temperature parameter from a received message.
        """
        self.__read_temperature = self._convert_2bytes_msg_to_value(self.__msg_datas)
    
    def __msg_set_fault_status(self):
        """
        Sets the value of the fault status parameter from a received message.
        """
        self.__fault_status = []
        fault_status_enum = [
            "FAN_FAIL",
            "OTP",
            "OVP",
            "OLP",
            "SHORT",
            "AC_FAIL",
            "OP_OFF",
            "HI_TEMP",
            "HV_OVP",
        ]
        
        # Combine bytes 2 and 3 to get the fault status value
        status = self._convert_2bytes_msg_to_value(self.__msg_datas)
        
        # Check each bit of the status value and append the corresponding fault status value to the list
        for i, flag in enumerate(fault_status_enum):
            if (status >> i) & 0x01 == 1:
                self.__fault_status.append(flag)
    
    def __msg_set_mfr_id1(self):
        self.__mfr_id1 = str(bytearray(self.__msg_datas[2:]), "ascii")
    
    def __msg_set_mfr_id2(self):
        self.__mfr_id2 = str(bytearray(self.__msg_datas[2:]), "ascii")
    
    def __msg_set_mfr_model1(self):
        self.__mfr_model1 = str(bytearray(self.__msg_datas[2:]), "ascii")
    
    def __msg_set_mfr_model2(self):
        self.__mfr_model2 = str(bytearray(self.__msg_datas[2:]), "ascii")
    
    def __msg_set_mfr_date(self):
        str_date = "20" + str(bytearray(self.__msg_datas[2:]), "ascii")
        date = datetime.strptime(str_date, "%Y%m%d")
        self.__mfr_date = datetime.strftime(date, "%Y-%m-%d")
    
    def __msg_set_mfr_serial(self):
        str_number = str(bytearray(self.__msg_datas[2:]), "ascii")
        self.__mfr_serial = int(str_number)
    
    def __msg_set_mfr_rev(self):
        self.__mfr_rev = []
        for i in self.__msg_datas[2:]:
            if i != 0xFF:
                self.__mfr_rev.append("Rev" + str(i/10))
    
    def __extract_and_set_factor(self, factor_index, shift_bits):
        """
        Extracts and sets the factor value based on the given index, shift bits, and min/max values.
        """
        factor_value = (self.__msg_datas[factor_index] >> shift_bits) & 0x0F
        if 3 < factor_value < 10:
            factor_value -= 7
        else:
            factor_value = 0
        return factor_value

    def __msg_set_scaling_factor(self):
        """
        Sets the values of the scaling factor parameters from a received message.
        """
        # Extract and set the Iin factor
        self.__rev_iout_factor = self.__extract_and_set_factor(5, 0)

        # Extract and set the temperature factor
        self.__temperature_factor = self.__extract_and_set_factor(4, 0)

        # Extract and set the fan speed factor
        self.__fan_speed_factor = self.__extract_and_set_factor(3, 4)

        # Extract and set the Vin factor
        self.__rev_vout_factor = self.__extract_and_set_factor(3, 0)

        # Extract and set the Iout factor
        self.__iout_factor = self.__extract_and_set_factor(2, 4)

        # Extract and set the Vout factor
        self.__vout_factor = self.__extract_and_set_factor(2, 0)
            
    def __msg_set_system_status(self):
        """
        Sets the system status from a received message.
        """
        self.__sys_status = []
        sys_status_enum = [
            ["SLAVE", "MASTER"],
            [None, "DC_OK"],
            [None, "PFC_OK"],
            [None, None],
            [None, "ADL_ON"],
            [None, "INITIAL_STATE"],
            ["EEPEROM_OK", None],
        ]
        
        # Combine bytes 2 and 3 to get the system status value
        status = self._convert_2bytes_msg_to_value(self.__msg_datas)
        # Check each bit of the status value and append the corresponding system status value to the list
        for i, flag in enumerate(sys_status_enum):
            if flag[(status >> i) & 0x01] is not None:
                self.__sys_status.append(flag[(status >> i) & 0x01])
                    
    def __msg_set_system_configs(self):
        """
        Sets the system configuration from a received message.
        """
        sys_config_options = [
        "DEFAULT_OFF",
        "DEFAULT_ON",
        "LAST_TIME_SET",
        None,
        ]
        self.__sys_configs = []
        # Combine bytes 2 and 3 to get the system configuration value
        config = self._convert_2bytes_msg_to_value(self.__msg_datas)
        
        # Check each bit of the configuration value and append the corresponding system configuration value to the list
        if config & 0x01 == 1:
            self.__sys_configs.append("CAN_CRTL")
        else:
            self.__sys_configs.append("SVR")
        
        sys_config_bits = (config >> 1) & 0x03
        option = sys_config_options[sys_config_bits]
        if option:
            self.__sys_configs.append(option)
        
    def __msg_set_rever_set_vout(self):
        """
        Sets the value of the set reverse Vout parameter from a received message.
        """
        self.__set_rever_vout = self._convert_2bytes_msg_to_value(self.__msg_datas)
    
    def __msg_set_rever_set_iout(self):
        """
        Sets the value of the set reverse Iout parameter from a received message.
        """
        self.__set_rever_iout = self._convert_2bytes_msg_to_value(self.__msg_datas)
    
    def __msg_set_bidirectional_configs(self):
        """
        Sets the bidirectional configuration from a received message.
        """
        self.__bidir_configs = []
        # Combine bytes 2 and 3 to get the bidirectional configuration value
        config = self._convert_2bytes_msg_to_value(self.__msg_datas)
        
        # Check each bit of the configuration value and append the corresponding bidirectional configuration value to the list
        if config & 0x01 == 1:
            self.__bidir_configs.append("CANBUS_CTRL")
        else:
            self.__bidir_configs.append("BIDERECT")

