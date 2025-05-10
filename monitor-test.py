#!/usr/bin/env python3
#
# Douglas Alden - 13 Mar 2024
# 

import minimalmodbus
from datetime import datetime
import string
import os
import json
import time

from prometheus_client import Histogram, CollectorRegistry, start_http_server, Gauge, Info

from prometheus_client.metrics_core import GaugeMetricFamily


# Modbus RTU device parameters
#port = '/dev/tty.usbmodem56EC0108501'
#port = '/dev/ttyS4'
port = '/dev/ttyACM0'
baudrate = 115200
databits = 8
parity = 'N'
stopbits = 1
address = 0x83  # Modbus device address


# Function Codes
READ_HOLDING_REGISTER = 0x03
READ_INPUT_REGISTER = 0x04
PRESET_SINGLE_REGISTER = 0x06

# Data Types
FAULT_STATUS = 0x40
READ_VIN = 0x50
READ_VOUT = 0x60
READ_IOUT = 0x61
CHG_STATUS = 0xB8
SYSTEM_STATUS = 0xC3
UPS_CONFIG = 0xD2
READ_VBAT = 0xD3
TIME_BUFFERING = 0xE4
UPS_DELAY_TIME = 0xE8
UPS_RESTART_TIME = 0xE9
READ_IBAT = 0xD4
TEMPERATURE = 0x62

DRS_METRICS = {
        0: {
            'name': 'VOUT',
            'meaning': 'Output voltage',
           },
        1: {
            'name': 'VIN',
            'meaning': 'Input voltage',
           },
        2: {
            'name': 'IOUT',
            'meaning': 'Output current',
           },
        3: {
            'name': 'VBAT',
            'meaning': 'Voltage of battery',
           },
        4: {
            'name': 'IBAT',
            'meaning': 'Charging or discharging current of battery',
           },
        5: {
            'name': 'TEMPERATURE',
            'meaning': 'Internal ambient temperature',
           },
    }

CHG_VARS = {
    0: {
        'name': "FULLM",
        'meaning': "Fully charged mode status: 0: 'NOT fully charged', 1: 'Fully charged'",
        },
    1: {
        'name': "CCM",
        'meaning': "Constant current mode status, 0: 'The charger NOT in constant current mode', 1: 'The charger in constant current mode'"
        },
    2: {
        'name': "CVM",
        'meaning': "Constant voltage mode status, 0: 'The charger NOT in constant voltage mode', 1: 'The charger in constant voltage mode'"
        },
    3: {
        'name': "FVM",
        'meaning': "Float mode status, 0: 'The charger NOT in float mode', 1: 'The charger in float mode'"
        },
    7: {
        'name': "DCM",
        'meaning': "Battery discharge mode, 0: 'Charging', 1: 'Discharging'"
        },
    11: {
        'name': "BTNC",
        'meaning': "Battery detection, 0: 'Battery detected', 1: 'NO battery detected'"
        }
    }


FAIL_VARS = {
    1: {
        'name': "OTP",
        'meaning': "Over temperature protection, 0: 'Normal internal temperature', 1: 'Abnormal internal temperature'"
        },
    2: {
        'name': "OVP",
        'meaning': "Output over-voltage protection, 0: 'Normal output voltage', 1: 'Abnormal output voltage'"
        },
    3: {
        'name': "OLP",
        'meaning': "Output over current protection, 0: 'Normal output current', 1: 'Abnormal output current'"
        },
    4: {
        'name': "SHORT",
        'meaning': "Short circuit protection, 0: 'Shorted circuit does not exist', 1: 'Shorted circuit protected'"
        },
    5: {
        'name': "AC_FAIL",
        'meaning': "AC abnormal flag, 0: 'Normal AC range', 1: 'Abnormal AC range'"
        },
    6: {
        'name': "OP_OFF",
        'meaning': "DC status, 0: 'DC turned on', 1: 'DC turned off'"
        },
    7: {
        'name': "HI_TEMP",
        'meaning': "High ambient temperature protection, 0: 'Normal ambient temperature', 1: 'Abnormal ambient temperature'"
        }
    }

def read_registers(instrument, register_address, number_of_bytes, functioncode):
    try:
        # Read bytes from the specified input register
        values = instrument.read_registers(register_address, number_of_bytes, functioncode)

        print(f'{hex(register_address)}: {values}')
        if (register_address == FAULT_STATUS):
            value = values[0]
        elif (register_address == READ_VIN):
            value = values[0]/10
        elif (register_address == READ_VOUT):
            value = values[0]/100
        elif (register_address == READ_IOUT):
            value = values[0]/100
        elif (register_address == CHG_STATUS):
            value = values[0]
        elif (register_address == SYSTEM_STATUS):
            value = values[0]
        elif (register_address == READ_VBAT):
            value = values[0]/100
        elif (register_address == UPS_CONFIG):
            value = values[0]
        elif (register_address == TIME_BUFFERING):
            value = values[0]
        elif (register_address == UPS_DELAY_TIME):
            value = values[0]
        elif (register_address == UPS_RESTART_TIME): 
            value = values[0]
        elif (register_address == READ_IBAT): 
            
            value = twos_comp(values[0],16)/100
        elif (register_address == TEMPERATURE): 
            value = values[0]/10

        return value

    except Exception as e:
        print(f"{e}")
        return -99999 

def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is


def getvars():

    # Create a minimalmodbus instrument
    instrument = minimalmodbus.Instrument(port, address)
    instrument.serial.baudrate = baudrate
    instrument.serial.bytesize = databits
    instrument.serial.parity = parity
    instrument.serial.stopbits = stopbits

    monitor_vars = {}
    monitor_vars['DRS_METRICS'] = {} 
    m = monitor_vars['DRS_METRICS']


    m['VOUT'] = read_registers(instrument, READ_VOUT, 2, READ_INPUT_REGISTER)
    m['VIN'] = read_registers(instrument, READ_VIN, 1, READ_INPUT_REGISTER)
    m['VBAT'] = read_registers(instrument, READ_VBAT, 2, READ_INPUT_REGISTER)
    m['IBAT'] = read_registers(instrument, READ_IBAT, 2, READ_INPUT_REGISTER)
    m['IOUT'] = read_registers(instrument, READ_IOUT, 2, READ_INPUT_REGISTER)
    m['TEMPERATURE'] = read_registers(instrument, TEMPERATURE, 1, READ_INPUT_REGISTER)


    # Check if AC is still online
    system_status = read_registers(instrument, FAULT_STATUS, 1, READ_HOLDING_REGISTER)

    
    monitor_vars['FAIL_VARS'] = {}
    if (system_status != -99999): # Value was read
        for fail_bit in FAIL_VARS.keys():
            status = (system_status >> fail_bit) & 0x01

            monitor_vars['FAIL_VARS'][FAIL_VARS[fail_bit]["name"]] = (status, ) 

    # Check if timeout buffer has been reached.
    chg_status = read_registers(instrument, CHG_STATUS, 1, READ_HOLDING_REGISTER)

    if (chg_status != -99999):  # Value was read

        monitor_vars['CHG_VARS'] = {}
        for chg_bit in CHG_VARS.keys():
            status = (chg_status >> chg_bit) & 0x01

            monitor_vars['CHG_VARS'][CHG_VARS[chg_bit]["name"]] = (status, ) 


    # Close the serial connection
    instrument.serial.close()
    return (monitor_vars)

class DRS_Collector(object):
    def __init__(self):
        self.state = {}

    def collect(self):
        metrics = {}
        current_metrics = getvars()

        for bit,metric in CHG_VARS.items():
            metrics[metric['name']] = GaugeMetricFamily(f"drs_charge{metric['name']}", metric['meaning'])
            metrics[metric['name']].add_metric([], 
                                                current_metrics['CHG_VARS'][metric['name']][0], )

        for bit,metric in FAIL_VARS.items():
            metrics[metric['name']] = GaugeMetricFamily(f"drs_fail_{metric['name']}", metric['meaning'])
            metrics[metric['name']].add_metric([], 
                                                current_metrics['FAIL_VARS'][metric['name']][0], )

        for bit,metric in DRS_METRICS.items():
            metrics[metric['name']] = GaugeMetricFamily(f"drs_metric_{metric['name']}", metric['meaning'])
            metrics[metric['name']].add_metric([], 
                                                current_metrics['DRS_METRICS'][metric['name']], )




        for key in metrics:
            yield metrics[key]
    

if __name__ == "__main__":
    registry = CollectorRegistry()
    registry.register(DRS_Collector())


    print (getvars())

