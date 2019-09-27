# sort of configuration file for the devices attached to the busess

# buses:
from RAISoft.buses.bus_visa import GPIBBus, SERIALBus
import visa
import serial

# instrument descriptions:
from RAISoft.instruments.TimeMeter import MainTimerClass
from RAISoft.instruments.TTi import PStsx3510P
from RAISoft.instruments.Oriel import Cornerstone130
from RAISoft.instruments.SRS import LockInSR830
from RAISoft.instruments.Agilent import A34401, A34401_4ohm, A34401_curr, A34401_volt, A34401_Pt100, A34401_temp, A33220_sinusoid, A33220_square, A34401_HAMAMATSU
from RAISoft.instruments.Keithley import Electrometer617, Electrometer617, SM2602_channel, SM2602_FET, SM2602_4PP
from RAISoft.instruments.PID import PIDHeater
from RAISoft.instruments.LCRbridge import LCRmeterHIOKI, LCRmeterHP
from RAISoft.instruments.composites import LCRmeterLockIn_Agilent,LCRmeterLockIn
from RAISoft.instruments.HAAKE import HAAKE_F6

class Clock(MainTimerClass):
    def __init__(self):
        MainTimerClass.__init__(self)
        return

class PowerSource(PStsx3510P):
    def __init__(self):
        BUS = SERIALBus (serial.Serial(port='COM1', 
                                       baudrate=9600, 
                                       bytesize=serial.EIGHTBITS, 
                                       parity=serial.PARITY_NONE, 
                                       stopbits=serial.STOPBITS_ONE, 
                                       timeout=0.6, 
                                       xonxoff=1, 
                                       rtscts=0, 
                                       interCharTimeout=None), 
                                    Echoed=False,
                                    Terminator='\n')
        PStsx3510P.__init__(self,BUS)
        return

class Monochromator(Cornerstone130):
    def __init__(self):
        BUS = SERIALBus (serial.Serial(port='COM2', 
                                       baudrate=9600, 
                                       bytesize=serial.EIGHTBITS, 
                                       parity=serial.PARITY_NONE, 
                                       stopbits=serial.STOPBITS_ONE, 
                                       timeout=0.6, 
                                       xonxoff=1, 
                                       rtscts=0, 
                                       interCharTimeout=None), 
                                    Echoed=True,
                                    Terminator='\n')
        Cornerstone130.__init__(self,BUS)
        return

#class Monochromator(Cornerstone130):
#    def __init__(self):
#        BUS = SERIALBus(visa.SerialInstrument('ASRL2', 
#                                               baud_rate=9600, 
#                                               data_bits=8, 
#                                               stop_bits=1, 
#                                               parity=visa.no_parity,
#                                               term_chars=None), 
#                        Echoed=True,
#                        Terminator='\n')
#        Cornerstone130.__init__(self,BUS)
#        return

class LockIn(LockInSR830):
    def __init__(self):
        MAVmask=16
        IfaceReadyMask=0
        CMDexecMask=2
        GPIBAddr = 8
        BUS = GPIBBus (visa.GpibInstrument("GPIB0::%d::INSTR" % GPIBAddr), MAVmask,IfaceReadyMask,CMDexecMask)
        LockInSR830.__init__(self,BUS)
        return
    
class FastVoltmeter(A34401_volt):
    def __init__(self):
        MAVmask=16
        IfaceReadyMask=0
        GPIBAddr = 22
        BUS = GPIBBus (visa.GpibInstrument("GPIB0::%d::INSTR" % GPIBAddr), MAVmask,IfaceReadyMask)
        A34401_volt.__init__(self, BUS)
        return

class HamamatsuPhotodiode(A34401_HAMAMATSU):
    def __init__(self):
        MAVmask=16
        IfaceReadyMask=0
        GPIBAddr = 22
        BUS = GPIBBus (visa.GpibInstrument("GPIB0::%d::INSTR" % GPIBAddr), MAVmask,IfaceReadyMask)
        A34401_HAMAMATSU.__init__(self, BUS)
        return


class Electrometer(Electrometer617):
    def __init__(self):
        MAVmask=8
        IfaceReadyMask=0
        GPIBAddr = 27
        BUS = GPIBBus (visa.GpibInstrument("GPIB0::%d::INSTR" % GPIBAddr), MAVmask,IfaceReadyMask)
        Electrometer617.__init__(self, BUS)
        return

 

class Thermocouple(A34401_temp):
    def __init__(self):
        A34401_temp.__init__(self, GPIBBus ('Pt100meter', IfaceReadyMask=0))
        return

class Thermometer(A34401_Pt100):
    def __init__(self):
        MAVmask=16
        IfaceReadyMask=0
        GPIBAddr = 25
        BUS = GPIBBus (visa.GpibInstrument("GPIB0::%d::INSTR" % GPIBAddr), MAVmask,IfaceReadyMask)
        A34401_Pt100.__init__(self, BUS)
        return

#class TemperatureRegPID_ITO(PIDHeater):
#    def __init__(self):
#        Valve = PowerSource()    # for powering the peltiers
#        Valve.set_amperes_limit(4.00) # Protect the peltiers
#        Sensor = Thermocouple()    # measure the temperature
#        PIDHeater.__init__(self,Valve,Sensor,Kp=1.5, Ti=12, Td=0.3, looptime=0.5)
#        return
    
class Thermostat(HAAKE_F6):
    def __init__(self):
        BUS = SERIALBus (serial.Serial(port='COM3', 
                                       baudrate=4800, 
                                       bytesize=serial.EIGHTBITS, 
                                       parity=serial.PARITY_NONE, 
                                       stopbits=serial.STOPBITS_ONE, 
                                       timeout=0.6, 
                                       xonxoff=0, 
                                       rtscts=1, 
                                       interCharTimeout=None), 
                                    Echoed=False,
                                    Terminator='\r')
        HAAKE_F6.__init__(self, BUS)
        return

class GeneratorSine(A33220_sinusoid):
    def __init__(self):
        MAVmask=16
        IfaceReadyMask=0
        GPIBAddr = 10
        BUS = GPIBBus (visa.GpibInstrument("GPIB0::%d::INSTR" % GPIBAddr), MAVmask,IfaceReadyMask)
        A33220_sinusoid.__init__(self, BUS)
        return

class GeneratorSquare(A33220_square):
    def __init__(self):
        MAVmask=16
        IfaceReadyMask=0
        GPIBAddr = 10
        BUS = GPIBBus (visa.GpibInstrument("GPIB0::%d::INSTR" % GPIBAddr), MAVmask,IfaceReadyMask)
        A33220_square.__init__(self, BUS)
        return
    
class LCR_LockIn_Agilent(LCRmeterLockIn_Agilent):
    def __init__(self):
        # init bus for LockIn
        MAVmask=16
        IfaceReadyMask=0
        CMDexecMask=2
        GPIBAddr = 8
        LockInBUS = GPIBBus (visa.GpibInstrument("GPIB0::%d::INSTR" % GPIBAddr), MAVmask,IfaceReadyMask,CMDexecMask)
        # init bus for sine generator
        MAVmask=16
        IfaceReadyMask=0
        GPIBAddr = 10
        SineBUS = GPIBBus (visa.GpibInstrument("GPIB0::%d::INSTR" % GPIBAddr), MAVmask,IfaceReadyMask)
        # init LCR device
        LCRmeterLockIn_Agilent.__init__(self, LockInBUS, SineBUS)
        return

class LCR_LockIn(LCRmeterLockIn):
    def __init__(self):
        # init bus for LockIn
        MAVmask=16
        IfaceReadyMask=0
        CMDexecMask=2
        GPIBAddr = 8
        LockInBUS = GPIBBus (visa.GpibInstrument("GPIB0::%d::INSTR" % GPIBAddr), MAVmask,IfaceReadyMask,CMDexecMask)
        # init bus for sine generator
        # init LCR device
        LCRmeterLockIn.__init__(self, LockInBUS)
        return
    
class LCR_HP(LCRmeterHP):
    def __init__(self):
        LCRmeterHP.__init__(self, GPIBBus ('HPLCR'))
        return
    
class LCR_HIOKI(LCRmeterHIOKI):
    def __init__(self):
        LCRmeterHIOKI.__init__(self, GPIBBus ('HIOKI'))
        return

class SMU_channelA(SM2602_channel):
    def __init__(self):
        MAVmask=16
        IfaceReadyMask=0
        GPIBAddr = 26
        BUS = GPIBBus (visa.GpibInstrument("GPIB0::%d::INSTR" % GPIBAddr), MAVmask,IfaceReadyMask)
        SM2602_channel.__init__(self, BUS, channel='a', NPLC=10)
        return
    
class SMU_channelB(SM2602_channel):
    def __init__(self):
        MAVmask=16
        IfaceReadyMask=0
        GPIBAddr = 26
        BUS = GPIBBus (visa.GpibInstrument("GPIB0::%d::INSTR" % GPIBAddr), MAVmask,IfaceReadyMask)
        SM2602_channel.__init__(self, BUS, channel='b', NPLC=10)
        return

class SMU_FET_tester(SM2602_FET):
    def __init__(self):
        MAVmask=16
        IfaceReadyMask=0
        GPIBAddr = 26
        BUS = GPIBBus (visa.GpibInstrument("GPIB0::%d::INSTR" % GPIBAddr), MAVmask,IfaceReadyMask)
        SM2602_FET.__init__(self, BUS, NPLC=10)
        return

class SMU_4PP_tester(SM2602_4PP):
    def __init__(self):
        MAVmask=16
        IfaceReadyMask=0
        GPIBAddr = 26
        BUS = GPIBBus (visa.GpibInstrument("GPIB0::%d::INSTR" % GPIBAddr), MAVmask,IfaceReadyMask)
        SM2602_4PP.__init__(self, BUS, NPLC=10)
        return

    