#####################################################################
#                                                                   #
# spinapi.py                                                        #
#                                                                   #
# Copyright 2013, Christopher Billington, Philip Starkey            #
#                                                                   #
# This file is part of the spinapi project                          #
# (see https://bitbucket.org/cbillington/spinapi )                  #
# and is licensed under the Simplified BSD License.                 #
# See the LICENSE.txt file in the root of the project               #
# for the full license.                                             #
#                                                                   #
#####################################################################

import os
import sys
import platform
import ctypes
import time
if sys.version_info[0] == 2:
    str = unicode

# Whether or not to tell the spincore library to write debug logfiles.
# User can set to False before calling any spinapi functions to disable debugging.
debug = False

this_folder = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))
def _checkloaded():
    global _spinapi
    try:    
        _spinapi
    except NameError:
        arch = platform.architecture()
        if arch == ('32bit', 'WindowsPE'):
            libname = 'spinapi.dll'
        elif arch == ('64bit', 'WindowsPE'):
            libname = 'spinapi64.dll'
        elif arch == ('32bit', 'ELF'):
            libname = os.path.join(this_folder, 'libspinapi.so')
        elif arch == ('64bit', 'ELF'):
            libname = os.path.join(this_folder, 'libspinapi64.so')

        _spinapi = ctypes.cdll.LoadLibrary(libname)
        # enable debugging if it's switched on by the module global:
        pb_set_debug(debug)

# Defines for different pb_instr instruction types
CONTINUE = 0
STOP = 1
LOOP = 2
END_LOOP = 3
JSR = 4
RTS = 5
BRANCH = 6
LONG_DELAY = 7
WAIT = 8
RTI = 9

# Defines for using different units of time
ns = 1.0
us = 1000.0
ms = 1000000.0
s  = 1000000000.0

# Defines for using different units of frequency
MHz = 1.0
kHz = .001
Hz = .000001

# Defines for start_programming
PULSE_PROGRAM  = 0
FREQ_REGS = 1
PHASE_REGS = 2

# Defines for enabling analog output
ANALOG_ON = 1
ANALOG_OFF = 0

# Defines for resetting the phase:
PHASE_RESET = 1
NO_PHASE_RESET = 0




def spinpts_get_version():
    _checkloaded()
    _spinapi.spinpts_get_version.restype = ctypes.c_char_p
    return _spinapi.spinpts_get_version()

def pb_get_firmware_id():
    _checkloaded()
    _spinapi.pb_get_firmware_id.restype = ctypes.c_uint
    return _spinapi.pb_get_firmware_id()
    
def pb_set_debug(debug):
    _checkloaded()
    _spinapi.pb_set_debug.restype = ctypes.c_int
    return _spinapi.pb_set_debug(ctypes.c_int(debug))

def pb_get_version():
    _checkloaded()
    _spinapi.pb_get_version.restype = ctypes.c_char_p
    return _spinapi.pb_get_version()

def pb_get_error():
    _checkloaded()
    _spinapi.pb_get_error.restype = ctypes.c_char_p
    return _spinapi.pb_get_error()

def pb_status_message():
    _checkloaded()
    _spinapi.pb_status_message.restype = ctypes.c_char_p
    message = _spinapi.pb_status_message()
    return message
  
def pb_read_status():
    _checkloaded()
    _spinapi.pb_read_status.restype = ctypes.c_uint32
    status = _spinapi.pb_read_status()
    
    # convert to reversed binary string
    # convert to binary string, and remove 0b
    status = bin(status)[2:]
    # reverse string
    status = status[::-1]
    # pad to make sure we have enough bits!
    status = status + "0000"
    
    return {"stopped":bool(int(status[0])),"reset":bool(int(status[1])),"running":bool(int(status[2])), "waiting":bool(int(status[3]))}
  
def pb_count_boards():
    _checkloaded()
    _spinapi.pb_count_boards.restype = ctypes.c_int
    result = _spinapi.pb_count_boards()
    if result == -1: raise RuntimeError(pb_get_error())  
    return result

def pb_select_board(board_num):
    _checkloaded()
    _spinapi.pb_select_board.restype = ctypes.c_int
    result = _spinapi.pb_select_board(ctypes.c_int(board_num))
    if result < 0: raise RuntimeError(pb_get_error())
    return result
                               
def pb_init():
    _checkloaded()
    _spinapi.pb_init.restype = ctypes.c_int
    result = _spinapi.pb_init()
    if result != 0: raise RuntimeError(pb_get_error())
    return result
    
def pb_core_clock(clock_freq):
    _checkloaded()
    _spinapi.pb_core_clock.restype = ctypes.c_void_p
    _spinapi.pb_core_clock(ctypes.c_double(clock_freq)) # returns void, so ignore return value.
                
def pb_start_programming(device):
    _checkloaded()
    _spinapi.pb_start_programming.restype = ctypes.c_int
    result = _spinapi.pb_start_programming(ctypes.c_int(device))
    if result != 0: raise RuntimeError(pb_get_error())
    return result
    
def pb_select_dds(dds):
    _checkloaded()
    _spinapi.pb_select_dds.restype = ctypes.c_int
    result = _spinapi.pb_select_dds(ctypes.c_int(dds))
    if result < 0: raise RuntimeError(pb_get_error())
    return result
    
def pb_set_phase(phase):
    _spinapi.pb_set_phase.restype = ctypes.c_int
    result = _spinapi.pb_set_phase(ctypes.c_double(phase))
    if result < 0: raise RuntimeError(pb_get_error())
    return result

def pb_set_freq(freq):
    _checkloaded()
    _spinapi.pb_set_freq.restype = ctypes.c_int
    result = _spinapi.pb_set_freq(ctypes.c_double(freq))
    if result < 0: raise RuntimeError(pb_get_error())
    return result

def pb_set_amp(amp, register):
    _checkloaded()
    _spinapi.pb_set_amp.restype = ctypes.c_int
    result = _spinapi.pb_set_amp(ctypes.c_float(amp),ctypes.c_int(register))
    if result < 0: raise RuntimeError(pb_get_error())
    return result

def pb_inst_pbonly(flags, inst, inst_data, length):
    _checkloaded()
    _spinapi.pb_inst_pbonly.restype = ctypes.c_int
    if isinstance(flags, str) or isinstance(flags, bytes):
        flags = int(flags[::-1],2)
    result = _spinapi.pb_inst_pbonly(ctypes.c_uint32(flags), ctypes.c_int(inst),
                                     ctypes.c_int(inst_data),ctypes.c_double(length))
    if result < 0: raise RuntimeError(pb_get_error())
    return result
    
def pb_inst_dds2(freq0,phase0,amp0,dds_en0,phase_reset0,
                 freq1,phase1,amp1,dds_en1,phase_reset1,
                 flags, inst, inst_data, length):
    """Gives a full instruction to the pulseblaster, with DDS included. The flags argument can be
       either an int representing the bitfield for the flag states, or a string of ones and zeros.
       Note that if passing in a string for the flag states, the first character represents flag 0.
       Eg.
       If it is a string: 
            flag: 0          12
                 '101100011111'
       
       If it is a binary number (or integer:
            flag:12          0
                0b111110001101
                3981    <---- integer representation
       """
    _checkloaded()
    _spinapi.pb_inst_dds2.restype = ctypes.c_int
    if isinstance(flags, str) or isinstance(flags, bytes):
        flags = int(flags[::-1],2)
    result = _spinapi.pb_inst_dds2(ctypes.c_int(freq0),ctypes.c_int(phase0),ctypes.c_int(amp0),
                                  ctypes.c_int(dds_en0),ctypes.c_int(phase_reset0),
                                  ctypes.c_int(freq1),ctypes.c_int(phase1),ctypes.c_int(amp1),
                                  ctypes.c_int(dds_en1),ctypes.c_int(phase_reset1),
                                  ctypes.c_int(flags),ctypes.c_int(inst),
                                  ctypes.c_int(inst_data),ctypes.c_double(length))
    if result < 0: raise RuntimeError(pb_get_error())
    return result

# More convenience functions:
def program_freq_regs(*freqs, **kwargs):
    call_stop_programming = kwargs.pop('call_stop_programming', True)
    pb_start_programming(FREQ_REGS)
    for freq in freqs:
        pb_set_freq(freq)
    if call_stop_programming:
        pb_stop_programming()
    if len(freqs) == 1:
        return 0
    else:
        return tuple(range(len(freqs)))

def program_phase_regs(*phases, **kwargs):
    call_stop_programming = kwargs.pop('call_stop_programming', True)
    pb_start_programming(PHASE_REGS)
    for phase in phases:
        pb_set_phase(phase)
    if call_stop_programming:
        pb_stop_programming()
    if len(phases) == 1:
        return 0
    else:
        return tuple(range(len(phases)))

def program_amp_regs(*amps):
    for i, amp in enumerate(amps):
        pb_set_amp(amp,i)
    if len(amps) == 1:
        return 0
    else:
        return tuple(range(len(amps)))

def pb_stop_programming():
    _checkloaded()
    _spinapi.pb_stop_programming.restype = ctypes.c_int
    result = _spinapi.pb_stop_programming()
    if result != 0: raise RuntimeError(pb_get_error())
    return result
    
def pb_start():
    _checkloaded()
    _spinapi.pb_start.restype = ctypes.c_int
    result = _spinapi.pb_start()
    if result != 0: raise RuntimeError(pb_get_error())
    return result
    
def pb_stop():
    _checkloaded()
    _spinapi.pb_stop.restype = ctypes.c_int
    result = _spinapi.pb_stop()
    if result != 0: raise RuntimeError(pb_get_error())
    return result
            
def pb_close():
    _checkloaded()
    _spinapi.pb_close.restype = ctypes.c_int
    result = _spinapi.pb_close()
    if result != 0: raise RuntimeError(pb_get_error())
    return result
    
def pb_reset():
    _checkloaded()
    _spinapi.pb_reset.restype = ctypes.c_int
    result = _spinapi.pb_reset()
    if result != 0: raise RuntimeError(pb_get_error())
    return result
    
def pb_write_default_flag(flags):
    _checkloaded()
    _spinapi.pb_write_register.restype = ctypes.c_int
    if isinstance(flags, str) or isinstance(flags, bytes):
        flags = int(flags[::-1],2)
    result = _spinapi.pb_write_register(ctypes.c_int(0x40000+0x08), ctypes.c_int(flags))
    if result != 0: raise RuntimeError(pb_get_error())
    return result

