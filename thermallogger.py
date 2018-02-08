import json 
import pandas as pd
from aardvark.aardvark_py3 import (aa_find_devices_ext,
                                  AA_PORT_NOT_FREE,
                                  aa_open, aa_i2c_pullup,
                                  AA_I2C_PULLUP_BOTH)

from aardvark.wrapper import AardvarkI2CWriteRead
import sys
import time
from keithley import Keithley, KeithleyNoConnection, KeithleyBadData

def create_aardvark_list():
    
    aardvark_list = {}

    (num, ports, ids) = aa_find_devices_ext(16, 16)

    for i in range(num):
        port      = ports[i]
        unique_id = ids[i]
 
        inuse = "(avail)"
        if (port & AA_PORT_NOT_FREE):
            inuse = "(in-use)"
            port  = port & ~AA_PORT_NOT_FREE

        if inuse == "(avail)":
            aardvark_list.update({port:unique_id})
    
    return aardvark_list

def create_single_transaction(address, tlm, name):
    transaction = {
        'address' : address,
        'cmd' : 0x10, # get tlm command 
        'data' : tlm,
        'delay' : 25,
        'bytes_to_read' : 2,
        'name' : name
    }
    return transaction

def generate_transactions(config):
    config = json.load(open(config))
    transaction_number = 1
    all_transactions = {}
    devices = config['devices']
    for device in devices:
        device_transactions = {}
        address = int(devices[device]['Address'], 16)
        tlm_cmds_list = devices[device]['TLE codes']
        for name, value in tlm_cmds_list.items():
            transaction = create_single_transaction(address, int(value, 16), name)
            device_transactions.update({('transaction' + str(transaction_number)) :transaction})
            transaction_number = transaction_number + 1
        
        all_transactions.update(device_transactions)

    return all_transactions

def open_aardvark(port):
    handle = aa_open(port)
    aa_i2c_pullup(handle, AA_I2C_PULLUP_BOTH)
    return handle

def create_instances(aardvark_list):
    instances = {}
    for port, unique_id in aardvark_list.items():
        serial_number = input('what is the serial number for the product attached to ' + str(unique_id))
        config = input('what config?')
        transaction_list = list(generate_transactions(config).values())
        handle = open_aardvark(port)
        keithley_channels_string = input('What channels are connected to this product e.g 1 2 3 5')
        keithley_channels = map(int, keithley_channels_string.split())
        instance = {serial_number:
        {
            "handle": handle,
            "Transactions": transaction_list,
            "keithley channels": keithley_channels
        }}
        instances.update(instance)
    
    return instances

def build_df(instance_list):
    column_list = []
    temperature_channels  = [19, 20]
    for instance in instance_list:
        serial_number = str(instance)
        transaction_list = instance_list[instance]["Transactions"]
        keithley_channel_list = instance_list[instance]['keithley channels']
        for transaction in transaction_list:
            tlm_name = transaction["name"]
            column_name = (serial_number, tlm_name)
            column_list.append(column_name)
        
        for channel in keithley_channel_list:
            channel_number = str(channel)
            column_name = (serial_number, channel_number)
            column_list.append(column_name)

    for channel in temperature_channels:
        channel_number = str(channel)
        column_name = ('Temperature', channel_number)
        column_list.append(column_name) 
    
    df = pd.DataFrame(columns=column_list)
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    return df

def run_tlm_log(df, instance_list, keithley):
    ind = len(df) + 1 
    temperature_channels  = [19, 20]
    for instance in instance_list:
        serial_number = str(instance)
        handle = instance_list[instance]['handle']
        transaction_list = instance_list[instance]["Transactions"]
        keithley_channel_list = instance_list[instance]['keithley channels']
        for transaction in transaction_list:
            tlm_name = transaction["name"]
            column_name = (serial_number, tlm_name)
            data_read, bytes_read, bytes_written = AardvarkI2CWriteRead(handle, transaction)
            data = byte_to_word(data_read)
            df.set_value(ind, column_name, data)
        
        for channel in keithley_channel_list:
            channel_number = str(channel)
            column_name = (serial_number, channel_number)
            data = keithley.channel[channel_number].getVoltageDC()
            df.set_value(ind, column_name, data)
    
    for channel in temperature_channels:
        channel_number = str(channel)
        column_name = ('Temperature', channel_number)
        data = keithley.channel[channel_number].getTemperature()
        df.set_value(ind, column_name, data)
         
def byte_to_word(bytes):
    return(bytes[0]<<8 |bytes[1])

def main():

    aardvark_list = create_aardvark_list()
    all_instances = create_instances(aardvark_list)
    df = build_df(all_instances)
    sleeptime = 10.0
    keithley_comm =  input('com')
    keithley = Keithley(comm=keithley_comm)
    while True:
        try:
            run_tlm_log(df, all_instances, keithley)
            start_time = time.time()
            while True:
                time.sleep(sleeptime - ((time.time() - start_time) % sleeptime))
        except KeyboardInterrupt:
            df.to_csv('thing.csv')
            sys.exit(0)

if __name__ == "__main__":
    main()

