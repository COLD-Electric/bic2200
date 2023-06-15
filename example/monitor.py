from bic2200.bic_set import Bic2200
import logging
import time
import can
import os

LOG_LEVEL = logging.INFO

if __name__ == '__main__':
    logging.basicConfig(level=LOG_LEVEL)
    # Create a CAN bus object with the canalystii interface and channel 0 at a bitrate of 250 kbps
    canbus_bic = can.interface.Bus(bustype="canalystii", channel=0, bitrate=250000)
    bic_device = Bic2200(canbus_bic)
    listener_bic = bic_device.boot()
    time.sleep(1)
    try:
        while True:
            d = bic_device.get_voltage_and_current()
            vout = d[0]
            iout = d[1]
            print(f"vout:{vout}")
            time.sleep(5)
    except KeyboardInterrupt:
        print("waiting for stopping...")
        try:
            bic_device.stop()
        except:
            logging.warning("device did not stop successfully")
        else:
            logging.info("device stop")
        os._exit(0)
        