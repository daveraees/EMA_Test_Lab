# this is script for testing of FET 
# Uses the Keithley Dual SourceMeter 2602 (GIPB addr 26) device to measure
# the source drain current-voltage characteristics at list of fixed Gates.


# project libraries imports:
# instruments:
from instruments.TimeMeter import MainTimerClass
#from instruments.Keithley import SM2602_sweepV
from instruments.Keithley import SM2602_channel, Electrometer6517
#from instruments.PID_ConBrio import PID_CBdriver
from instruments.Oriel import Monochromator
from instruments.Agilent import A34401_volt

# file-output libraries
from Output.Output import OutputHandler

# define and ACTIVATE the instruments
Stopwatch = MainTimerClass()
Stopwatch.Activate()

Channel = Electrometer6517(27)
Channel.Activate()

Gate = SM2602_channel(26, channel='a', NPLC=2)
Gate.Activate()

#PeltierP = PID_CBdriver(TCchannel=1, count=20)
#PeltierP.Activate()

Filter = Monochromator(4)
Filter.Activate()

LightMeter = A34401_volt(22)
LightMeter.Activate()

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

def observe (duration):
    Stopwatch.zeroTimer()
    while Stopwatch.getSinceLastZeroed() < duration:    # observe the temperature variables for about 5 min, wait for the Temp to stabilize
            Stopwatch.Wait(0.05)
            Stopwatch.Measure()
            Channel.Measure()
            Gate.Measure()
            LightMeter.Measure()
            Data.acquireData()

def Test (SDvoltage, Gvolage, timeSTABIL, Wavelength, timeON, timeOFF, cyclesN=1):
    # initialization
    report ('Starting new irradiation kinetics, at lambda= %d' % Wavelength)
    Filter.set_wave(Wavelength)
    Stopwatch.Wait(1)
    Filter.close_shutter()
    Gate.set_volts(Gvolage)
    Channel.set_volts(SDvoltage)
    Gate.set_output_on()
    Channel.set_output_on()
    Filter.close_shutter()
    Stopwatch.Wait(5)
    Filter.set_wave(Wavelength)
    # stabilization of the SD current at given voltages
    
    report('starting the stabilization for %d seconds' % timeSTABIL)
    Stopwatch.zeroTimer()
    observe(timeSTABIL)
    Data.separateData()

    for cycle in range(cyclesN):
        report('starting the irradiation cycle No. %d' % cycle)
       
        # Start irradiating the sample
        report('starting the irradiation for %d seconds' % timeON)
        Filter.open_shutter()
        observe(timeON)
        Data.separateData()
        
        # Start the measurement in dark
        report('starting the dark kinetics for %d seconds' % timeOFF)
        Filter.close_shutter()
        observe(timeOFF)
        Data.separateData()
        
    report('Experiment finished')
#end
