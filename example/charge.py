from bic2200.bic_set import Bic2200
import sys, getopt, os
#from htbibms.bms import HtbiBms
import logging
import can
import time

HELP_MSG = "\
    usage:\n\
    python charge.py -v <voltage> -i <current> [Option]\n\
    Option:\n\
    --max_charge charge maximum charging capacity\n\
    --debug debug mode\n\
    -h, --help help"

if __name__ == '__main__':
    log_level = logging.INFO
    total_charge_ah = 0
    charge_vout = None
    charge_iout = None
    
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "-h-v:-i:", ["help","max_charge=","debug"])
    except getopt.GetoptError:
        print(HELP_MSG)
        os._exit(0)
    for opt, arg in opts:
        if opt == "-v":
            charge_vout = float(arg)
        elif opt =="-i":
            charge_iout = float(arg)
        elif opt == "--max_charge":
            total_charge_ah = int(arg)
        elif opt == "--debug":
            log_level = logging.DEBUG
        else:
            print(HELP_MSG)
            os._exit(0)
    
    if charge_vout is None or charge_iout is None:
        print(HELP_MSG)
        os._exit(0)
    
    logging.basicConfig(level=log_level)
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
        