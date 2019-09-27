# project libraries imports:
# instruments:
from instruments.Devices import Electrometer, Clock
#from instruments.Keithley import Electrometer617
#from instruments.Agilent import A34401_4ohm

# file-output libraries
from Output.Output import OutputHandler

################################################################
##  Here begins the initialization of devices ##################
################################################################
    
# define and ACTIVATE the instruments
Stopwatch = Clock()
Stopwatch.Activate()
Elmeter = Electrometer()
Elmeter.Activate()
# don`t forget to activate the instruments before opening the output file:
Data = OutputHandler()
Data.setDataFileName()
    

def Test(voltages, acquizDelay=0.1, voltStepDelay=5):
    """ simple current-voltage characteristics measurement """
    ################################################################
    ##  Here begins the experimetal part ###########################
    ################################################################
    
    # switch on the voltage source:
    Elmeter.set_output_on()
    Elmeter.zero_check('off')
    
    for voltage in voltages:
        Elmeter.set_volts(voltage)
        Stopwatch.zeroTimer()
        while Stopwatch.getSinceLastZeroed() < voltStepDelay:
            Stopwatch.Wait(acquizDelay)
            Stopwatch.Measure()
            Elmeter.Measure()
            Data.acquireData()
        Data.separateData()
    
    Elmeter.zero_check('on')
    Elmeter.set_output_off()


# some heplful functions:

def careful_voltage(voltage, stepNumber, delay):
    """divides the voltage step in number of smaller ones linearly"""
    from numpy import linspace
    actualV = Elmeter.get_volts()
    smoothedSteps = linspace(actualV, voltage, stepNumber)
    for volt in smoothedSteps:
        Elmeter.set_volts(volt)
        Stopwatch.Wait(delay)

def observe (duration, delay=0.5):
    """general repeating data acquizition cycle"""
    Stopwatch.zeroTimer()
    while Stopwatch.getSinceLastZeroed() < duration:    # observe the temperature variables for about 5 min, wait for the Temp to stabilize
            Stopwatch.Wait(delay)
            Stopwatch.Measure()
            Elmeter.Measure()
            Data.acquireData()

import time
def report(message, file='report.info'):
    date = time.asctime(time.localtime())
    message = ('%(date)s: %(message)s \n' % \
            {'date':date, 'message':message})
    print message
    f = open(file, 'a')
    f.write(message)
    f.close()

def Test2(lowVoltages, highVoltages, voltStepDelayLONG=10, voltStepDelaySHORT=None):
    if voltStepDelaySHORT == None:
        voltStepDelaySHORT = voltStepDelayLONG
    # switch on the voltage source:
    report ('Starting NEW EXPERIMENT - Current-Voltage Characteristic NOW')
    Elmeter.set_output_on()
    
    for voltage in lowVoltages:
        report ('appling new voltage: %f' % voltage)
        careful_voltage(voltage, 5, 1.5)    # adjust voltage
        report ('stabilization at new voltage: %f seconds begins NOW' % voltStepDelayLONG)
        observe (duration=voltStepDelayLONG, delay=0.5) # measure
        Data.separateData()
    
    for voltage in highVoltages:
        report ('appling new voltage: %f' % voltage)
        careful_voltage(voltage, 5, 1.5)    # adjust voltage
        report ('stabilization at new voltage: %f seconds begins NOW' % voltStepDelaySHORT)
        observe (duration=voltStepDelaySHORT, delay=0.5) # measure
        Data.separateData()
    
    #Elmeter.set_output_off()