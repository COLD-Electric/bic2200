from bic2200.bic_set import Bic2200
import sys, getopt, os
#from htbibms.bms import HtbiBms
import logging
import can
import time

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    total_charge_ah = 0
    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, "-h-v:-i:", ["help","max_charge="])
    for opt, arg in opts:
        if opt == "-v":
            charge_vout = float(arg)
        elif opt =="-i":
            charge_iout = float(arg)
        elif opt == "--max_charge":
            total_charge_ah = int(arg)
        else:
            print("usage:")
            print("python charge.py -v <voltage> -i <current> [Option]")
            print("Option:")
            print("--max_charge charge maximum charging capacity")
            os._exit(0)
    try:
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
        bic_device.set_vout(charge_vout) #set voltage
        bic_device.set_iout(charge_iout) #set current
        bic_device.charge() # set charge mode
        bic_device.start() # start charging
        chargeAh = 0
    except NameError:
        print("usage:")
        print("python charge.py -v <voltage> -i <current> [Option]")
        print("Option:")
        print("--max_discharge charge maximum charging capacity")
        os._exit(0)
    try:
        if total_charge_ah > 0:
            while chargeAh < total_charge_ah * 3600:
                d = bic_device.get_voltage_and_current()
                vout = d[0]
                iout = d[1]
                chargeAh = chargeAh + iout * 5
                logging.info(f"vout:{vout}\tiout:{iout}\tcharge process:{round(chargeAh / (total_charge_ah * 3600) * 100, 2)}%")
                time.sleep(5)
            bic_device.stop()
            while True:
                d = bic_device.get_voltage_and_current()
                vout = d[0]
                iout = d[1]
                logging.info(f"vout:{vout}\tiout:{iout}")
                time.sleep(5)
        else:
            while True:
                d = bic_device.get_voltage_and_current()
                vout = d[0]
                iout = d[1]
                chargeAh = chargeAh + iout * 5
                logging.info(f"vout:{vout}\tiout:{iout}\tcharge process:{round(chargeAh/3600, 2)}AH")
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
        