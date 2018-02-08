import json 
import pandas as pd
from aardvark.aardvark_py3 import *
from aardvark.wrapper import *
import sys
import time
from twisted.internet import reactor, task

def create_addvark_list():
    
    addvark_list = {}

    (num, ports, ids) = aa_find_devices_ext(16, 16)

    for i in range(num):
        port      = ports[i]
        unique_id = ids[i]
 
        inuse = "(avail)"
        if (port & AA_PORT_NOT_FREE):
            inuse = "(in-use)"
            port  = port & ~AA_PORT_NOT_FREE

        if inuse == "(avail)":
            addvark_list.update({port:unique_id})
    
    return addvark_list

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


def open_addvark(port):
    handle = aa_open(port)
    aa_i2c_pullup(handle, AA_I2C_PULLUP_BOTH)
    return handle

def create_instances(addvark_list):
    instances = {}
    for port, unique_id in addvark_list.items():
        serial_number = 1 #input('what is the serial number for the product attached to ' + str(unique_id))
        config = 'C:\Git\ThermalLogger\eps thermal config.json' #input('what config?')
        transaction_list = list(generate_transactions(config).values())
        handle = open_addvark(port)
        instance = {serial_number:
        {
            "handle": handle,
            "Transactions": transaction_list
        }}
        instances.update(instance)
    
    return instances

def build_df(instance_list):
    column_list = []
    for instance in instance_list:
        serial_number = str(instance)
        transaction_list = instance_list[instance]["Transactions"]
        for transaction in transaction_list:
            tlm_name = transaction["name"]
            column_name = (serial_number, tlm_name)
            column_list.append(column_name)
    
    df = pd.DataFrame(columns=column_list)
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    return df

def run_tlm_log(df, instance_list):
    ind = len(df) + 1 
    for instance in instance_list:
        serial_number = str(instance)
        handle = instance_list[instance]['handle']
        transaction_list = instance_list[instance]["Transactions"]
        for transaction in transaction_list:
            tlm_name = transaction["name"]
            column_name = (serial_number, tlm_name)
            data_read, bytes_read, bytes_written = AardvarkI2CWriteRead(handle, transaction)
            data = byte_to_word(data_read)
            df.set_value(ind, column_name, data)

def byte_to_word(bytes):
    return(bytes[0]<<8 |bytes[1])


def main():

    addvark_list = create_addvark_list()
    if len(addvark_list) < 1:
        print('no addvarks detected')
        sys.exit(0)
    else:
        all_instances = create_instances(addvark_list)
        df = build_df(all_instances)
        sleeptime = 10.0
        l = task.LoopingCall(run_tlm_log(df, all_instances))
        l.start(sleeptime)
        while True:
            try:
                reactor.run()
            except KeyboardInterrupt:
                df.to_csv('thing2.csv')
                sys.exit(0)


if __name__ == "__main__":
    main()

