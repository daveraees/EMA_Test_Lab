
# project libraries imports:
# instruments:
from instruments.TimeMeter import MainTimerClass
#from instruments.Keithley import SM2602_sweepV
from instruments.Keithley import SM2602_channel
# file-output libraries
from Output.Output import OutputHandler

# define and ACTIVATE the instruments
Stopwatch = MainTimerClass()
Stopwatch.Activate()

Wire = SM2602_channel('dualSmeter', channel='a', NPLC=2)
Wire.Activate()

Piezo = SM2602_channel('dualSmeter', channel='b', NPLC=2)
Piezo.Activate()
# don`t forget to activate the instruments before opening the output file:
Data = OutputHandler()
Data.setDataFileName('test.dat')


import time
def report(message, file='report.info'):
    date = time.asctime(time.localtime())
    message = ('%(date)s: %(message)s \n' % \
            {'date':date, 'message':message})
    print message,
    f = open(file, 'a')
    f.write(message)
    f.close()



#begin
report ('Starting new scanning (Measurement of I-V characteristic for various extensions of piezo Element)')
piezoVoltage = 10.0    # start with the piezo element maximally extended
wireVoltage = 0.001    # voltage for the wire break detection 
thresholdCurrent = 1e-4    # threshold current to detect wire break (broken if the current is lower than that)
Piezo.set_volts(piezoVoltage)
Piezo.set_output_on()
Piezo.Measure()
timeout = 600    # timeout for breaking the wire by hand

junctionBroken = False # indicator of break detection
Stopwatch.zeroTimer()
Wire.set_volts(wireVoltage) # apply the voltage 1 mV to the wire 
Wire.set_output_on()
while True:    # break detecton loop, not recorded
    Stopwatch.Wait(0.02)
    #Stopwatch.Measure()
    #Wire.Measure()
    #Data.acquireData()
    #actualCurrent = Data.analysis.average_last(key="aCurrent(A)",number=1)
    actualCurrent = Wire.get_amperes()
    report('PIEZO=%.3fV; wire: I=%e A' % (piezoVoltage, actualCurrent))
    if (actualCurrent < thresholdCurrent):
        report ('the wire break detected, proceeding with piezo retraction')
        Wire.beep()
        junctionBroken = True
        break    # finish the measurement if the wire broke
    if Stopwatch.getSinceLastZeroed() > timeout:
        junctionBroken = False
        report ('the timeout elapsed. no wire break detected. Stopping the experiment')
        break    # finish the measurement anyway if the timeout elapsed

if junctionBroken:
    #Data.separateData()
    shift = 0
    while not (piezoVoltage <= 0):
        piezoVoltage = piezoVoltage - (shift / 50.0)
        if piezoVoltage < 0.0:
            break
        Piezo.set_volts(piezoVoltage)
        shift = shift + 1
        Stopwatch.Wait(0.02)
        Stopwatch.Measure()
        Piezo.Measure()
        Wire.MeasureISweepV(start=1e-4, stop=1e-3, number=6, delay=0.01)
        Data.analysis.mark_from()
        Data.acquireData()
        Data.analysis.mark_to()
        Data.separateData()
        (intercept, slope, first_coordinate, r, tt, stderr) = Data.analysis.linear_regres_marked("aCurrent(A)", "aVoltage(V)")
        report('PIEZO=%.3fV; wire: Res=%e ohm, stderr= %e' % (piezoVoltage, slope,stderr))

report('Experiment finished')
#end
