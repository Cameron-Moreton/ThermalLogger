#==========================================================================
# Aardvark Interface Library
#--------------------------------------------------------------------------
# Copyright (c) 2002-2008 Total Phase, Inc.
# All rights reserved.
# www.totalphase.com
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# - Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
# - Neither the name of Total Phase, Inc. nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATp, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#--------------------------------------------------------------------------
# To access Aardvark devices through the API:
#
# 1) Use one of the following shared objects:
#      aardvark.so      --  Linux shared object
#      aardvark.dll     --  Windows dynamic link library
#
# 2) Along with one of the following language modules:
#      aardvark.c/h     --  C/C++ API header file and interface module
#      aardvark_py.py   --  Python API
#      aardvark.bas     --  Visual Basic 6 API
#      aardvark.cs      --  C# .NET source
#      aardvark_net.dll --  Compiled .NET binding
#==========================================================================

#==========================================================================
# VERSION
#==========================================================================
AA_API_VERSION    = 0x050a   # v5.10
AA_REQ_SW_VERSION = 0x050a   # v5.10

import os
import sys
import ctypes as c

from array import array, ArrayType
import struct

api = c.cdll.LoadLibrary('aardvark.dll')
if not api:
    print('Unable to load aardvark.dll')
    exit(0)
else:
    AA_LIBRARY_LOADED = True

#==========================================================================
# HELPER FUNCTIONS
#==========================================================================
def malloc_u08 (n):  return c.pointer((c.c_uint8*n)())
def malloc_u16 (n):  return c.pointer((c.c_uint16*n)())
def malloc_u32 (n):  return c.pointer((c.c_uint32*n)())
def malloc_u64 (n):  return c.pointer((c.c_uint64*n)())
def malloc_s08 (n):  return c.pointer((c.c_int8*n)())
def malloc_s16 (n):  return c.pointer((c.c_int16*n)())
def malloc_s32 (n):  return c.pointer((c.c_int32*n)())
def malloc_s64 (n):  return c.pointer((c.c_int64*n)())
def malloc_f32 (n):  return c.pointer((c.c_float*n)())
def malloc_f64 (n):  return c.pointer((c.c_double*n)())

def pointer_u08 (a):  return c.pointer((c.c_uint8*len(a))(*a))
def pointer_u16 (a):  return c.pointer((c.c_uint16*len(a))(*a))
def pointer_u32 (a):  return c.pointer((c.c_uint32*len(a))(*a))
def pointer_u64 (a):  return c.pointer((c.c_uint64*len(a))(*a))
def pointer_s08 (a):  return c.pointer((c.c_int8*len(a))(*a))
def pointer_s16 (a):  return c.pointer((c.c_int16*len(a))(*a))
def pointer_s32 (a):  return c.pointer((c.c_int32*len(a))(*a))
def pointer_s64 (a):  return c.pointer((c.c_int64*len(a))(*a))
def pointer_f32 (a):  return c.pointer((c.c_float*len(a))(*a))
def pointer_f64 (a):  return c.pointer((c.c_double*len(a))(*a))

def array_u08 (p, n):  return array('B', [x for x in p.contents[:n]])
def array_u16 (p, n):  return array('H', [x for x in p.contents[:n]])
def array_u32 (p, n):  return array('I', [x for x in p.contents[:n]])
def array_u64 (p, n):  return array('K', [x for x in p.contents[:n]])
def array_s08 (p, n):  return array('b', [x for x in p.contents[:n]])
def array_s16 (p, n):  return array('h', [x for x in p.contents[:n]])
def array_s32 (p, n):  return array('i', [x for x in p.contents[:n]])
def array_s64 (p, n):  return array('L', [x for x in p.contents[:n]])
def array_f32 (p, n):  return array('f', [x for x in p.contents[:n]])
def array_f64 (p, n):  return array('d', [x for x in p.contents[:n]])

#==========================================================================
# STATUS CODES
#==========================================================================
# All API functions return an integer which is the result of the
# transaction, or a status code if negative.  The status codes are
# defined as follows:
# enum AardvarkStatus
# General codes (0 to -99)
AA_OK                        =    0
AA_UNABLE_TO_LOAD_LIBRARY    =   -1
AA_UNABLE_TO_LOAD_DRIVER     =   -2
AA_UNABLE_TO_LOAD_FUNCTION   =   -3
AA_INCOMPATIBLE_LIBRARY      =   -4
AA_INCOMPATIBLE_DEVICE       =   -5
AA_COMMUNICATION_ERROR       =   -6
AA_UNABLE_TO_OPEN            =   -7
AA_UNABLE_TO_CLOSE           =   -8
AA_INVALID_HANDLE            =   -9
AA_CONFIG_ERROR              =  -10

# I2C codes (-100 to -199)
AA_I2C_NOT_AVAILABLE         = -100
AA_I2C_NOT_ENABLED           = -101
AA_I2C_READ_ERROR            = -102
AA_I2C_WRITE_ERROR           = -103
AA_I2C_SLAVE_BAD_CONFIG      = -104
AA_I2C_SLAVE_READ_ERROR      = -105
AA_I2C_SLAVE_TIMEOUT         = -106
AA_I2C_DROPPED_EXCESS_BYTES  = -107
AA_I2C_BUS_ALREADY_FREE      = -108

# SPI codes (-200 to -299)
AA_SPI_NOT_AVAILABLE         = -200
AA_SPI_NOT_ENABLED           = -201
AA_SPI_WRITE_ERROR           = -202
AA_SPI_SLAVE_READ_ERROR      = -203
AA_SPI_SLAVE_TIMEOUT         = -204
AA_SPI_DROPPED_EXCESS_BYTES  = -205

# GPIO codes (-400 to -499)
AA_GPIO_NOT_AVAILABLE        = -400

# I2C bus monitor codes (-500 to -599)
AA_I2C_MONITOR_NOT_AVAILABLE = -500
AA_I2C_MONITOR_NOT_ENABLED   = -501

AA_PORT_NOT_FREE = 0x8000

#==========================================================================
# GENERAL API
#==========================================================================

# Get a list of ports to which Aardvark devices are attached.
#
# This function is the same as aa_find_devices() except that
# it returns the unique IDs of each Aardvark device.  The IDs
# are guaranteed to be non-zero if valid.
#
# The IDs are the unsigned integer representation of the 10-digit
# serial numbers.
def aa_find_devices_ext (devices, unique_ids):

    if not AA_LIBRARY_LOADED: return AA_INCOMPATIBLE_LIBRARY

    ports = malloc_u16(devices)
    uids  = malloc_u32(unique_ids)

    ret = api.c_aa_find_devices_ext(devices, ports, unique_ids, uids)
    return ret, array_u16(ports, ret), array_u32(uids, ret)

# Open the Aardvark port.
#
# The port number is a zero-indexed integer.
#
# The port number is the same as that obtained from the
# aa_find_devices() function above.
#
# Returns an Aardvark handle, which is guaranteed to be
# greater than zero if it is valid.
#
# This function is recommended for use in simple applications
# where extended information is not required.  For more complex
# applications, the use of aa_open_ext() is recommended.
def aa_open (port_number):
    """usage: Aardvark return = aa_open(int port_number)"""

    if not AA_LIBRARY_LOADED: return AA_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.c_aa_open(port_number)

# Close the Aardvark port.
def aa_close (aardvark):
    """usage: int return = aa_close(Aardvark aardvark)"""

    if not AA_LIBRARY_LOADED: return AA_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.c_aa_close(aardvark)

# Set the I2C bit rate in kilohertz.  If a zero is passed as the
# bitrate, the bitrate is unchanged and the current bitrate is
# returned.
def aa_i2c_bitrate (aardvark, bitrate_khz):
    """usage: int return = aa_i2c_bitrate(Aardvark aardvark, int bitrate_khz)"""

    if not AA_LIBRARY_LOADED: return AA_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.c_aa_i2c_bitrate(aardvark, bitrate_khz)

# Configure the I2C pullup resistors.
# This is only supported on hardware versions >= 2.00
AA_I2C_PULLUP_NONE = 0x00
AA_I2C_PULLUP_BOTH = 0x03
AA_I2C_PULLUP_QUERY = 0x80

def aa_i2c_pullup (aardvark, pullup_mask):
    """usage: int return = aa_i2c_pullup(Aardvark aardvark, u08 pullup_mask)"""

    if not AA_LIBRARY_LOADED: return AA_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.c_aa_i2c_pullup(aardvark, pullup_mask)

# Configure the target power pins.
# This is only supported on hardware versions >= 2.00
AA_TARGET_POWER_NONE = 0x00
AA_TARGET_POWER_BOTH = 0x03
AA_TARGET_POWER_QUERY = 0x80

def aa_target_power (aardvark, power_mask):
    """usage: int return = aa_target_power(Aardvark aardvark, u08 power_mask)"""

    if not AA_LIBRARY_LOADED: return AA_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.c_aa_target_power(aardvark, power_mask)

# enum AardvarkI2cFlags
AA_I2C_NO_FLAGS          = 0x00
AA_I2C_10_BIT_ADDR       = 0x01
AA_I2C_COMBINED_FMT      = 0x02
AA_I2C_NO_STOP           = 0x04
AA_I2C_SIZED_READ        = 0x10
AA_I2C_SIZED_READ_EXTRA1 = 0x20

# Read a stream of bytes from the I2C slave device.
def aa_i2c_read (aardvark, slave_addr, flags, n_bytes):
    """usage: (int return, u08[] data_in) = aa_i2c_read(Aardvark aardvark, u16 slave_addr, AardvarkI2cFlags flags, u08[] data_in)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not AA_LIBRARY_LOADED: return AA_INCOMPATIBLE_LIBRARY
    # Call API function
    p_data_in = malloc_u08(n_bytes)
    (_ret_) = api.c_aa_i2c_read(aardvark, slave_addr, flags, n_bytes, p_data_in)
    data_in = array_u08(p_data_in, _ret_)
    # data_in post-processing
    return (_ret_, data_in)

# Write a stream of bytes to the I2C slave device.
def aa_i2c_write (aardvark, slave_addr, flags, data_out):
    """usage: int return = aa_i2c_write(Aardvark aardvark, u16 slave_addr, AardvarkI2cFlags flags, u08[] data_out)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function."""

    if not AA_LIBRARY_LOADED: return AA_INCOMPATIBLE_LIBRARY
    # data_out pre-processing
    num_bytes = len(data_out)
    p_data_out = pointer_u08(data_out)
    # Call API function
    return api.c_aa_i2c_write(aardvark, slave_addr, flags, num_bytes, p_data_out)

# Sleep for the specified number of milliseconds
# Accuracy depends on the operating system scheduler
# Returns the number of milliseconds slept
def aa_sleep_ms (milliseconds):
    """usage: u32 return = aa_sleep_ms(u32 milliseconds)"""

    if not AA_LIBRARY_LOADED: return AA_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.c_aa_sleep_ms(milliseconds)

#==========================================================================
# SPI API
#==========================================================================
# Set the SPI bit rate in kilohertz.  If a zero is passed as the
# bitrate, the bitrate is unchanged and the current bitrate is
# returned.
def aa_spi_bitrate (aardvark, bitrate_khz):
    """usage: int return = aa_spi_bitrate(Aardvark aardvark, int bitrate_khz)"""

    if not AA_LIBRARY_LOADED: return AA_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.c_aa_spi_bitrate(aardvark, bitrate_khz)

# Change the output polarity on the SS line.
#
# Note: When configured as an SPI slave, the Aardvark will
# always be setup with SS as active low.  Hence this function
# only affects the SPI master functions on the Aardvark.
# enum AardvarkSpiSSPolarity
AA_SPI_SS_ACTIVE_LOW  = 0
AA_SPI_SS_ACTIVE_HIGH = 1

def aa_spi_master_ss_polarity (aardvark, polarity):
    """usage: int return = aa_spi_master_ss_polarity(Aardvark aardvark, AardvarkSpiSSPolarity polarity)"""

    if not AA_LIBRARY_LOADED: return AA_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.c_aa_spi_master_ss_polarity(aardvark, polarity)

# These configuration parameters specify how to clock the
# bits that are sent and received on the Aardvark SPI
# interface.
#
#   The polarity option specifies which transition
#   constitutes the leading edge and which transition is the
#   falling edge.  For example, AA_SPI_POL_RISING_FALLING
#   would configure the SPI to idle the SCK clock line low.
#   The clock would then transition low-to-high on the
#   leading edge and high-to-low on the trailing edge.
#
#   The phase option determines whether to sample or setup on
#   the leading edge.  For example, AA_SPI_PHASE_SAMPLE_SETUP
#   would configure the SPI to sample on the leading edge and
#   setup on the trailing edge.
#
#   The bitorder option is used to indicate whether LSB or
#   MSB is shifted first.
#
# See the diagrams in the Aardvark datasheet for
# more details.
# enum AardvarkSpiPolarity
AA_SPI_POL_RISING_FALLING = 0
AA_SPI_POL_FALLING_RISING = 1

# enum AardvarkSpiPhase
AA_SPI_PHASE_SAMPLE_SETUP = 0
AA_SPI_PHASE_SETUP_SAMPLE = 1

# enum AardvarkSpiBitorder
AA_SPI_BITORDER_MSB = 0
AA_SPI_BITORDER_LSB = 1

# Configure the SPI master or slave interface
def aa_spi_configure (aardvark, polarity, phase, bitorder):
    """usage: int return = aa_spi_configure(Aardvark aardvark, AardvarkSpiPolarity polarity, AardvarkSpiPhase phase, AardvarkSpiBitorder bitorder)"""

    if not AA_LIBRARY_LOADED: return AA_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.c_aa_spi_configure(aardvark, polarity, phase, bitorder)

# Write a stream of bytes to the downstream SPI slave device.
def aa_spi_write (aardvark, data_out, data_in):
    """usage: (int return, u08[] data_in) = aa_spi_write(Aardvark aardvark, u08[] data_out, u08[] data_in)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not AA_LIBRARY_LOADED: return AA_INCOMPATIBLE_LIBRARY
    # data_out pre-processing
    out_num_bytes = len(data_out)

    if isinstance(data_in, int):
        in_num_bytes = data_in
    else:
        in_num_bytes = len(data_in)

    p_data_in = malloc_u08(in_num_bytes)
    p_data_out = pointer_u08(data_out)

    # Call API function
    (_ret_) = api.c_aa_spi_write(aardvark, out_num_bytes, p_data_out, in_num_bytes, p_data_in)
    # data_in post-processing
    data_in = array_u08(p_data_in, _ret_)
    return (_ret_, data_in)

