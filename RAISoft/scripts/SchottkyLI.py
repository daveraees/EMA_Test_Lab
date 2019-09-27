# This is script for measurement of 
# Schottky barrier capacity dependence on DC Bias Voltage
# using an LockIn

# 
# project libraries imports:
# instruments:
from instruments.Devices import Clock, LCR_LockIn_Agilent
# file-output libraries
from Output.Output import OutputHandler

# define and ACTIVATE the instruments
Stopwatch = Clock()
Stopwatch.Activate()

# The Capacity Measurements is performed by Lock In Amplifier
LCR = LCR_LockIn_Agilent()
LCR.Activate()

# don`t forget to activate the instruments before opening the output file:
Data = OutputHandler()
Data.setDataFileName()



def observe (duration, delay):
    Stopwatch.zeroTimer()
    while Stopwatch.getSinceLastZeroed() < duration:    # observe the temperature variables for about 5 min, wait for the Temp to stabilize
            Stopwatch.Wait(delay)
            Stopwatch.Measure()
            LCR.Measure()
            Data.acquireData()


def Test(DCvoltages, DCwait, ACvoltage, Frequences, FreqWait):
    
    Data.report('Starting the Schottky barrier measurement')
    
    # set the AC signal source in the LOCKIN amplifier
    
    LCR.setFreq(1.0e+3)
    LCR.setACLevelV(ACvoltage)
    LCR.setBias(2*ACvoltage)
    LCR.set_output_on()
    
    for Freq in Frequences:
        Data.report(('Applying frequency %f' % Freq ))
        LCR.setFreq(Freq)
        #Sine.set_offset(ACvoltage)
        Stopwatch.Wait(FreqWait)
        LCR.auto_gain()
        for DCvoltage in DCvoltages:
            Data.report(('Applying DC voltage %f' % DCvoltage ))
            LCR.setBias(DCvoltage)
            observe(DCwait, 1)
            Data.separateData()
    Data.report('Experiment finished')
    return

