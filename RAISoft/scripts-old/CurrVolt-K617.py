#!/usr/bin/python
"""
this is script meant to be executable file 
allowing to perform: Current-voltage characteristic using Keithley K617 model
at stabilized temperature
"""



# Here Edit eleriment parameters :

# create the list of testing voltages
# import functions to create arrays of test voltages
from numpy import linspace, logspace, log10, hstack
lowVoltages = linspace(0.05,0.45,9)
startVoltage=0.5
finalVoltage=3
pointNumber=20
highVoltages = logspace(log10(startVoltage),log10(finalVoltage),pointNumber)
voltages = hstack([lowVoltages,highVoltages])

# checkout the list of testing voltages
print voltages

#define the temperature ramp parameters
rampStep = 4    # the height of ramp in degrees of Celsius
rampTime = 400.0  # time of ramp in seconds
setpoint = 30     # base temperature of the ramping steps
################################################################
##  Here begins the initialization of devices ##################
################################################################

# project libraries imports:
# instruments:
from instruments.TimeMeter import MainTimerClass
from instruments.Keithley import Electrometer617
from instruments.PID import PIDHeater
from instruments.Agilent import A34401_4ohm

# file-output libraries
from Output.Output import OutputHandler

# define and ACTIVATE the instruments
Stopwatch = MainTimerClass()
Stopwatch.Activate()
Electrometer = Electrometer617('Electrometer')
Electrometer.Activate()
PeltierP = PIDHeater() # temperature regulation
PeltierP.Activate()
Platinum = A34401_4ohm('FastMultimeter')
Platinum.Activate()
# don`t forget to activate the instruments before opening the output file:
Data = OutputHandler()
Data.setDataFileName()


################################################################
##  Here begins the experimetal part ###########################
################################################################

# switch on the voltage source:
Electrometer.set_output_on()

# initialize PID temperature regulation
PeltierP.set_PID_params(Kp=1.788, Ti=12.8, Td=0.313, looptime=0.1)
PeltierP.setNew_setpoint(value=setpoint, tolerance=0.2, evalPeriod=300)
PeltierP.startRegulation()
PeltierP.waitForSetpoint()


for voltage in voltages:
    Electrometer.set_volts(voltage)
    Stopwatch.Wait(5)
    Stopwatch.Measure()
    Platinum.Measure()
    PeltierP.Measure()
    Data.acquireData()

