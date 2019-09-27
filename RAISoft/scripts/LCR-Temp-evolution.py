

from instruments.TimeMeter import MainTimerClass
from instruments.LCRbridge import LCRmeterHP
# file-output libraries
from Output.Output import OutputHandler



# define and ACTIVATE the instruments
Stopwatch = MainTimerClass()
Stopwatch.Activate()

LCR = LCRmeterHP('HPLCR', Params=['CP(F)','RP(ohm)'])
LCR.Activate()

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
            LCR.Measure()
            Data.acquireData()

def Test(Frequency, ACamplitude, Time, Delay):
    """ testing the time evolution of AC parameters"""
    
    report ('Starting new time-measurement of AC parameters, using HP LCR bridge')
    
    LCR.setFreq(Frequency)
    LCR.setACLevelV(ACamplitude)
    observe(Time,Delay)
    
    