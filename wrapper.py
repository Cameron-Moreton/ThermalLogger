from aardvark_py3 import *
from clint.textui import puts, indent, colored

def InitialiseAardvark():
  puts(colored.magenta("Detecting Aardvark adapters:"))

  # Find all the attached devices
  (num, ports, unique_ids) = aa_find_devices_ext(16, 16)

  with indent(2, quote=colored.cyan('|')):
    if num > 0:
        puts ("%d device(s) found:" % num)

        # Print the information on each device
        for i in range(num):
            port      = ports[i]
            unique_id = unique_ids[i]

            # Determine if the device is in-use
            inuse = "(avail)"
            if (port & AA_PORT_NOT_FREE):
                inuse = "(in-use)"
                port  = port & ~AA_PORT_NOT_FREE

            # Display device port number, in-use status, and serial number
            with indent(4):
              puts ("port = %d   %s  (%04d-%06d)" % \
                  (port, inuse, unique_id / 1000000, unique_id % 1000000))
    else:
        puts (colored.red("No devices found."))

    try:
        puts ( "Connecting to device on port %d." % port)
        handle = aa_open(port)
        if (handle <= 0):
            puts (colored.red ("Unable to open Aardvark device on port %d" % port))
            puts (colored.red ("Error code = " + colored.white(handle)))
            sys.exit()

        aa_i2c_pullup (handle, AA_I2C_PULLUP_BOTH)

    except:
        puts (colored.red ( "You may need to connect an Aardvark!"))
        sys.exit()

  puts("\n\n")        
  return handle

def AardvarkSetBaudRate(handle, baud_rate):
  return aa_i2c_bitrate(handle, baud_rate)

def AardvarkI2CWriteRead(handle, transaction_details):
  return _AardvarkI2CWriteRead(
    handle, 
    transaction_details['address'],
    transaction_details['cmd'],
    transaction_details['data'],
    transaction_details['bytes_to_read'] if 'bytes_to_read' in transaction_details else 0,
    transaction_details['delay'] if 'delay' in transaction_details else 0)

def ArrayToInt(a):
  # Convert Array into Big Int
  value=0
  for v in a:
    value = value << 8
    value = value + v

  return value

def IntToArray(i):
  result = []
  if not(isinstance(i, list)):
    i = [i]
  else:
    i.reverse()

  for d in i:
    if (d==0):
      result.append(0)
    else:
      while d:
        result.append(d&0xFF)
        d >>= 8

  result.reverse()
  return result

def _AardvarkI2CWriteRead(handle, addr, command, data, bytes_to_read, delay):

    message = [command]
    if not(data is None):
      data_array = IntToArray(data[:]) if (isinstance(data, (list, tuple))) else IntToArray(data) # Format Data Field
      message.extend(data_array)

    data_out = array('B', message)
    bytes_written = aa_i2c_write(handle, addr, AA_I2C_NO_FLAGS, data_out)
    aa_sleep_ms(delay)

    if bytes_to_read:
      (bytes_read, data_in) = aa_i2c_read(
          handle, addr, AA_I2C_NO_FLAGS, bytes_to_read)

      return (data_in, bytes_read, bytes_written)
    else:
      return (0, 0, 0)

def CloseAardvark(handle):
  aa_close(handle)
