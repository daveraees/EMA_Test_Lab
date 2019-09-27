"""
This script slowly increases the voltage and measures the resulting current
and simultaneously monitors the capacity of teh sample
"""


from instruments.TimeMeter import MainTimerClass
from instruments.Agilent import A34401_volt, A34401_curr
from instruments.LCRbridge import LCRmeterHIOKI
from instruments.TTi import PStsx3510P

# file-output libraries
from Output.Output import OutputHandler

# define and ACTIVATE the instruments
Stopwatch = MainTimerClass()
Stopwatch.Activate()

VoltageSource = PStsx3510P('PowerSourceTTi')
VoltageSource.Activate()

#LCR = LCRmeterHIOKI('HIOKI', Params=['CP(F)','RP(ohm)'])
#LCR.Activate()

# to record the voltage applied to the sample
Voltmeter = A34401_volt('Voltmeter')
Voltmeter.Activate()

# to record the current flowing through the sample
Ameter = A34401_curr('FastMultimeter')
Ameter.Activate()

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


def observe (duration, delay=0.5):
    """general repeating data acquizition cycle"""
    Stopwatch.zeroTimer()
    while Stopwatch.getSinceLastZeroed() < duration:    # observe the temperature variables for about 5 min, wait for the Temp to stabilize
            Stopwatch.Wait(delay)
            Stopwatch.Measure()
            Voltmeter.Measure()
            Ameter.Measure()
            #LCR.Measure()
            Data.acquireData()



def Test(voltages, acquizDelay=0.1, voltStepDelay=5):
    """ current-voltage characteristics measurement 
    (with electrolyte contact during electrolytic oxidation/ reduction 
    Important parameters of the test 
    voltages      # list of testin voltages, in Volts
    acquizDelay   # data acquizition delay in seconds
    voltStepDelay # delay between voltage steps in seconds
    """
    report ('Starting new I-V-Cap wet capacity measurement')
    
    VoltageSource.set_volts(0.0)
    VoltageSource.set_output_off()
    Stopwatch.Wait(voltStepDelay)
    VoltageSource.set_amperes_limit(0.4)
    VoltageSource.Measure()
    #LCR.setFreq(frequency)
    VoltageSource.set_output_on()
    
    for voltage in voltages:
        VoltageSource.set_volts(voltage)
        #VoltageSource.Measure()
        Stopwatch.zeroTimer()
        observe(voltStepDelay,acquizDelay)
        #Data.separateData()
    
    report ('Experiment Finished' )
    VoltageSource.set_output_off()
    