# This is script for measurement of Photocurrent spectera
# 
# project libraries imports:
# instruments:
from instruments.Devices import Clock, Monochromator, Electrometer, LockIn,FastVoltmeter, PowerSource
#from instruments.TimeMeter import MainTimerClass
#from instruments.Keithley import Electrometer6517
#from instruments.PID_ConBrio import PID_CBdriver
#from instruments.Oriel import Monochromator
#from instruments.Agilent import A34401_volt
#from instruments.SRS import LockInSR830
#from instruments.TTi import PStsx3510P
# file-output libraries
from Output.Output import OutputHandler

# define and ACTIVATE the instruments
Stopwatch = Clock()
Stopwatch.Activate()

# The electrometer serves only as a voltage source.
Channel = Electrometer()
Channel.Activate()

#PeltierP = PID_CBdriver(TCchannel=1, count=20)
#PeltierP.Activate()

Filter = Monochromator()
Filter.Activate()

LightMeter = FastVoltmeter()
LightMeter.Activate()

# The modulated photocurrent is detected by Lock In Amplifier
LI = LockIn() # The Lock In amplifier
LI.Activate()

Lamp = PowerSource()
#Lamp.Activate()


# don`t forget to activate the instruments before opening the output file:
Data = OutputHandler()
Data.setDataFileName()


import time
def report(message, file='report.info'):
    date = time.asctime(time.localtime())
    message = ('%(date)s: %(message)s \n' % \
            {'date':date, 'message':message})
    print message,
    f = open(file, 'a')
    f.write(message)
    f.close()

def observe (duration, delay):
    Stopwatch.zeroTimer()
    while Stopwatch.getSinceLastZeroed() < duration:    # observe the temperature variables for about 5 min, wait for the Temp to stabilize
            Stopwatch.Wait(delay)
            Stopwatch.Measure()
            LI.Measure()
            Channel.Measure()
            LightMeter.Measure()
            Data.acquireData()

def Test(DCvoltage, Wavelengths, LampVolt, WaitDC, WaitWL, WaitDAQ):
    report('starting the photocurrent spectra measurement from %(from)d to %(to)d nm'  % \
            {'from':Wavelengths[0], 'to':Wavelengths[-1]})
    Filter.close_shutter()
    Channel.set_volts(DCvoltage)
    Channel.set_output_on()
    Lamp.set_volts(LampVolt)
    Lamp.set_amperes_limit(10)
    Lamp.set_output_on()
    Stopwatch.Wait(WaitDC)
    Channel.Measure()
    Lamp.Measure()
    Filter.open_shutter()

    for wl in Wavelengths:
        Filter.set_wave(wl)
        Filter.Measure()
        observe(WaitWL,WaitDAQ)
        Data.separateData()
    
    Channel.set_output_off()
    Lamp.set_output_off()
    Filter.close_shutter()
    report('finished the photocurrent spectra measurement')
    