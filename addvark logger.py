import json 
import pandas 
from aardvark.aardvark_py3 import *

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

def open_addvark(port):
    handle = aa_open(port)
    aa_i2c_pullup(handle, AA_I2C_PULLUP_BOTH)
    return handle


def create_single_transaction(address, tlm):
    transaction = {
        'address' : address,
        'cmd': 0x10, # get tlm command 
        'data': tlm,
        'delay': 25,
        'bytes_to_read': 2
    }
    return transaction


def generate_transactions(config):
    all_transactions = []
    for device in config['devices']:
        device_transactions = []
        address = device['address']
        tlm_cmds_list = device['TLE codes']
        for value in tlm_cmds_list:
            transaction = create_single_transaction(address, va)



a = create_addvark_list()
print(a)
for x, y in a.items():
    open_addvark(x)
    print('i have opened ' + str(x) + ' it has the id ' + str(y))



    