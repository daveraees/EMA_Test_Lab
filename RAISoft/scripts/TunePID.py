# Script for estimation of the Constants of the PID regulation
# by transinent probing of the system up and down withouth feedback

from instruments.Devices import Clock, Thermocouple, PowerSource
# file-output libraries
from Output.Output import OutputHandler

Stopwatch = Clock()
Stopwatch.Activate()

TC = Thermocouple()
TC.Activate()

PS = PowerSource()
PS.Activate()

# don`t forget to activate the instruments before opening the output file:
Data = OutputHandler()
Data.setDataFileName()


def TestOpenLoop(Voltage1, Voltage2, WaitTime):
    PS.set_output_on()
    PS.set_volts(Voltage1)
    Stopwatch.Wait(1)
    #PS.Measure()
    Stopwatch.zeroTimer()
    while Stopwatch.getSinceLastZeroed() < WaitTime:    # observe the temperature variables for about 5 min, wait for the Temp to stabilize
            Stopwatch.Wait(0.1)
            Stopwatch.Measure()
            PS.Measure()
            TC.Measure()
            Data.acquireData()
    
    PS.set_volts(Voltage2)
    #PS.Measure()
    Stopwatch.zeroTimer()
    while Stopwatch.getSinceLastZeroed() < WaitTime:    # observe the temperature variables for about 5 min, wait for the Temp to stabilize
            Stopwatch.Wait(0.1)
            Stopwatch.Measure()
            PS.Measure()
            TC.Measure()
            Data.acquireData()
    
    PS.set_volts(Voltage1)
    #PS.Measure()
    Stopwatch.zeroTimer()
    while Stopwatch.getSinceLastZeroed() < WaitTime:    # observe the temperature variables for about 5 min, wait for the Temp to stabilize
            Stopwatch.Wait(0.1)
            Stopwatch.Measure()
            PS.Measure()
            TC.Measure()
            Data.acquireData()
