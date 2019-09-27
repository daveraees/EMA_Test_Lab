#!/usr/bin/python
"""
Script for test of the Constants of the PID regulation
"""

#define the PID regulation parameters:
Gain = 1.788          # regulation gain    
Tinteg = 12.8    # integration time    (in seconds)
Tderiv = 0.313    # derivative time    (in seconds)
LoopTime = 0.1    # time between consequent regulation iterations (in seconds)
Tolerance = 0.2    # absolute (+-) tolerance of the regulator 
                    #to claim the setpoint "reached"   (in degrees)
Evaluation = 200    #amount of time in seconds    
                    #which the regulator must keep the 
                    #temperature within the tolerance 
                    #around the setpoint before it can be claimed 
                    #as setpoint "reached"

#define the temperature test setpoints
startTemp=15    #in degrees
finalTemp=10    #(in degrees)
pointNumber=2    # positive integer number :]
from numpy import linspace, logspace, log10, hstack
temperatures = linspace(startTemp,finalTemp,pointNumber)
print temperatures

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
PeltierP = PIDHeater() # temperature regulation
PeltierP.Activate()
Platinum = A34401_4ohm('FastMultimeter')
Platinum.Activate()
# don`t forget to activate the instruments before opening the output file:
Data = OutputHandler()
Data.setDataFileName()

PeltierP.set_PID_params(Kp=Gain, Ti=Tinteg, Td=Tderiv, looptime=LoopTime)
PeltierP.startRegulation()

for temperature in temperatures:
    PeltierP.setNew_setpoint(value=temperature, tolerance=Tolerance, evalPeriod=Evaluation)
    Stopwatch.zeroTimer()
    while Stopwatch.getSinceLastZeroed() < stabilizationTime:    # observe the temperature variables for about 5 min, wait for the Temp to stabilize
        Stopwatch.Wait(0.1)
        Stopwatch.Measure()
        Platinum.Measure()
        PeltierP.Measure()
        Data.acquireData()
    Data.separateData()


