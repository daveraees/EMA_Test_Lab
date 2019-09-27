# This script is for testing kinetics of photocurrent during irradiation 
# 


# project libraries imports:
# instruments:
from instruments.Devices import Clock, Monochromator, Electrometer, FastVoltmeter, PowerSource

#from instruments.TimeMeter import MainTimerClass
#from instruments.Keithley import Electrometer617
#from instruments.PID_ConBrio import PID_CBdriver
#from instruments.Agilent import A34401_volt
#from instruments.TTi import PStsx3510P

# file-output libraries
from Output.Output import OutputHandler

# define and ACTIVATE the instruments
Stopwatch = Clock()
Stopwatch.Activate()

Channel = Electrometer()
Channel.Activate()

#PeltierP = PID_CBdriver(TCchannel=1, count=20)
#PeltierP.Activate()

LightMeter = FastVoltmeter()
LightMeter.Activate()

Lamp = PowerSource()
Lamp.Activate()

Filter = Monochromator()
Filter.Activate()

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
            LightMeter.Measure()
            Data.acquireData()

def Test (SDvoltage, timeSTABIL, timeON, timeOFF, LampVoltages, Wavelength):
    # initialization
    report ('Starting new irradiation kinetics')
    Filter.set_wave(Wavelength)
    Filter.close_shutter()
    Lamp.set_amperes_limit(10.0)
    Lamp.set_volts(LampVoltages[0])
    Lamp.set_output_on()
    Lamp.Measure()
    Stopwatch.Wait(1)
    Channel.set_volts(SDvoltage)
    Channel.set_output_on()
    Stopwatch.Wait(5)
    Filter.Measure()
        # stabilization of the current at given voltage
    report('starting the stabilization for %d seconds' % timeSTABIL)
    Stopwatch.zeroTimer()
    observe(timeSTABIL)
    Data.separateData()

    for lampVolt in LampVoltages:
        report('starting the irradiation with lamp at %f Volts' % lampVolt)
        Lamp.set_volts(lampVolt)
        Stopwatch.Wait(1)    # wait for stabilisation of the voltage in the source
        Lamp.Measure()
        Filter.open_shutter()
        #Lamp.set_output_on()
        # Start irradiating the sample
        report('starting the irradiation for %d seconds' % timeON)
        observe(timeON)
        Data.separateData()
        
        # Start the measurement in dark
        report('starting the dark kinetics for %d seconds' % timeOFF)
        Filter.close_shutter()
        #Lamp.set_output_off()
        #Lamp.set_volts(0.0)
        observe(timeOFF)
        Data.separateData()
    report('Experiment finished')
    Lamp.set_output_off()
    Channel.set_output_off()
    Filter.close_shutter()
#end
