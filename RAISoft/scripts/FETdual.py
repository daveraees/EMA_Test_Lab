# this is script for testing of FET 
# Uses the Keithley Dual SourceMeter 2602 (GIPB addr 26) device to measure
# the source drain current-voltage characteristics at list of fixed Gates.


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

Channel = SM2602_channel('dualSmeter', channel='a', NPLC=10)
Channel.Activate()

Gate = SM2602_channel('dualSmeter', channel='b', NPLC=10)
Gate.Activate()

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

def IVscan(voltages, wait):
    for Vsd in voltages:
            Channel.set_volts(Vsd)
            Stopwatch.Wait(wait)
            # make the measurement
            Gate.Measure()
            Channel.Measure()
            Stopwatch.Measure()
            Data.acquireData()

def Test (SDvoltages, Gvoltages, SDwait, Gwait):
    # initialization
    report ('Starting new FET measurement of I-V characteristic S-D for various Gate voltages')
    Channel.set_volts(0.0)
    Gate.set_volts(0.0)
    Gate.set_output_on()
    Channel.set_output_on()
    Stopwatch.zeroTimer()
    # Actual testing algorithm
    for Vgate in Gvoltages:
        report ('applying Gate voltage = %0.3f V' % Vgate)
        Gate.set_volts(Vgate)   
        Stopwatch.Wait(Gwait)
        IVscan(SDvoltages, SDwait)
        Data.separateData()
    # in the case of multiple temperatures:
    
    Gate.set_output_off()
    Channel.set_output_off()
    report('Experiment finished')
#end

def FastOutput (start, stop, number, delay, Gvolages, Gwait):
    report ('Starting new FET measurement of output characteristic for various Gate voltages')
    Channel.set_volts(0.0)
    Gate.set_volts(0.0)
    Gate.set_output_on()
    Channel.set_output_on()
    Stopwatch.zeroTimer()
    # Actual testing algorithm
    for Vgate in Gvolages:
            report ('applying Gate voltage = %0.3f V' % Vgate)
            Gate.set_volts(Vgate)   
            Stopwatch.Wait(Gwait)
            Gate.Measure()
            Channel.MeasureISweepV(start, stop, number, delay)
            Data.acquireData()
            Data.separateData()
        # in the case of multiple temperatures:
    Gate.set_output_off()
    Channel.set_output_off()
    report('Experiment finished')

def Transfer (SDvoltages, Gvoltages, SDwait, Gwait):
    report ('Starting new FET measurement of transfer characteristic for various S-D voltages')
    Channel.set_volts(0.0)
    Gate.set_volts(0.0)
    Gate.set_output_on()
    Channel.set_output_on()
    Stopwatch.zeroTimer()
    # Actual testing algorithm
    for Vsd in SDvoltages:
            report ('applying S-D voltage = %0.3f V' % Vsd)
            Channel.set_volts(Vsd)   
            Stopwatch.Wait(SDwait)
            # now scan set Gate voltages
            for Vg in Gvoltages:
                Gate.set_volts(Vg)
                Stopwatch.Wait(Gwait)
                # make the measurement
                Gate.Measure()
                Channel.Measure()
                Stopwatch.Measure()
                Data.acquireData()
            Data.separateData()
        # in the case of multiple temperatures:
    Gate.set_output_off()
    Channel.set_output_off()
    report('Experiment finished')