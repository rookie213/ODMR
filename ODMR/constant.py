PULSE_PROGRAM  =0
FREQ_REGS      =1

PHASE_REGS     =2
TX_PHASE_REGS  =2
PHASE_REGS_1   =2

RX_PHASE_REGS  =3
PHASE_REGS_0   =3

# These are names used by RadioProcessor
COS_PHASE_REGS =51
SIN_PHASE_REGS =50

# For specifying which device in pb_dds_load
DEVICE_SHAPE =0x099000
DEVICE_DDS   =0x099001

#Defines for enabling analog output
ANALOG_ON       =1
ANALOG_OFF      =0
TX_ANALOG_ON    =1
TX_ANALOG_OFF   =0
RX_ANALOG_ON    =1
RX_ANALOG_OFF   =0

#Defines for status bits
STATUS_STOPPED  = 1
STATUS_RESET    =2
STATUS_RUNNING  =4
STATUS_WAITING  =8
STATUS_SCANNING =16

PARAM_ERROR =-99

#Variables for max number of registers (Currently the same across models) THIS NEEDS TO BE WEEDED OUT!!! any occurances should be replaced with board[cur_board].num_phase2, etc.
MAX_PHASE_REGS =16
MAX_FREQ_REGS =16


#  SpinPTS Includes & Defines

ERROR_STR_SIZE	    =25
 
BCDBYTEMASK	=0x0F0F0F0F

ID_MHz100		=0x0
ID_MHz10		=0x1  
ID_MHz1			=0x2
ID_kHz100		=0x3
ID_kHz10		=0x4
ID_kHz1			=0x5
ID_Hz100		=0x6
ID_Hz10			=0x7
ID_Hz1			=0x8
ID_pHz			=0x9
ID_latch    	        =0xA
ID_UNUSED		=0xF
 
PHASE_INVALID		=0x100
FREQ_ORANGE		=0x101

DWRITE_FAIL		=0x200
DEVICE_OPEN_FAIL	=0x201
NO_DEVICE_FOUND		=0x202

