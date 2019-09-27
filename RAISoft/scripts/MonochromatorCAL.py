# This is script for measurement of monochromator calibration
# 
# project libraries imports:
# instruments:
from instruments.Devices import Clock, Monochromator,  FastVoltmeter

# file-output libraries
from Output.Output import OutputHandler

# define and ACTIVATE the instruments
Stopwatch = Clock()
Stopwatch.Activate()

Filter = Monochromator()
Filter.Activate()

LightMeter = FastVoltmeter()
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

def observe (duration, delay):
    Stopwatch.zeroTimer()
    while Stopwatch.getSinceLastZeroed() < duration:    # observe the temperature variables for about 5 min, wait for the Temp to stabilize
            Stopwatch.Wait(delay)
            Stopwatch.Measure()
            LI.Measure()
            Channel.Measure()
            LightMeter.Measure()
            Data.acquireData()

def Test(Wavelengths, WaitWL):
    
    report('Starting test of monochromator calibration')
    Filter.open_shutter()
    Filter.set_wave(Wavelengths[0])
    #Stopwatch.Wait(20)
    for wl in Wavelengths:
        Filter.set_wave(wl)
        Filter.Measure()
        Stopwatch.Wait(WaitWL)
        Stopwatch.Measure()
        LightMeter.Measure()
        Data.acquireData()
        
    Filter.close_shutter()