from bic2200.bic_set import Bic2200
#from htbibms.bms import HtbiBms
import can
import time

TOTAL_CHARGE_AH = 40
CHARGE_VOUT = 24
DISCHARGE_VOUT = 20

if __name__ == '__main__':
    # Create a CAN bus object with the canalystii interface and channel 0 at a bitrate of 250 kbps
    canbus_bic = can.interface.Bus(bustype="canalystii", channel=0, bitrate=250000)
    bic_device = Bic2200(canbus_bic)
    listener_bic = bic_device.boot()
    '''
    packs = [6]
    canbus_bms = can.interface.Bus(bustype="canalystii",channel=1, bitrate=500000)
    bms_device = HtbiBms(canbus_bms, packs)
    listerner_bms = bms_device.boot()
    
    bms_device.clear_pf()
    bms_device.start()
    '''
    time.sleep(5)
    bic_device.set_vout(CHARGE_VOUT) #set voltage
    bic_device.set_iout(DISCHARGE_VOUT) #set current
    bic_device.charge() # set charge mode
    bic_device.start() # start charging
    chargeAh = 0
    
    while chargeAh < TOTAL_CHARGE_AH * 3600:
       d = bic_device.get_voltage_and_current()
       vout = d[0]
       iout = d[1]
       chargeAh = chargeAh + iout * 5
       print(f"vout:{vout}\tiout:{iout}\tcharge process:{round(chargeAh / (TOTAL_CHARGE_AH * 3600) * 100, 2)}%")
       time.sleep(5)
    bic_device.stop()
    
    while True:
        d = bic_device.get_voltage_and_current()
        vout = d[0]
        iout = d[1]
        print(f"vout:{vout}\tiout:{iout}")
        time.sleep(5)