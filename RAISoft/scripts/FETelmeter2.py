# this is script for testing of FET 
# Uses the Keithley Dual SourceMeter 2602 (GIPB addr 26) device to measure
# the source drain current-voltage characteristics at list of fixed Gates.


# project libraries imports:
# instruments:
from instruments.TimeMeter import MainTimerClass
#from instruments.Keithley import SM2602_sweepV
from instruments.Keithley import Electrometer617, Electrometer6517
#from instruments.PID_ConBrio import PID_CBdriver

# file-output libraries
from Output.Output import OutputHandler

# define and ACTIVATE the instruments
Stopwatch = MainTimerClass()
Stopwatch.Activate()

Gate = Electrometer617('Electrometer2')
Gate.Activate()

Channel = Electrometer6517('Electrometer')
Channel.Activate()


#PeltierP = PID_CBdriver(TCchannel=1, count=20)
#PeltierP.Activate()

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

def IVscan(voltages, wait, roomTemp):
    for Vsd in voltages:
            Channel.set_volts(Vsd)
            Stopwatch.Wait(wait)
            # make the measurement
            Gate.Measure()
            Channel.Measure()
            Stopwatch.Measure()
            #if not roomTemp:
                #PeltierP.Measure()
            Data.acquireData()

def GateLoop(startingVoltage, stoppingVoltage, scanDuration, scanRate, loopDelay):
    rampInterval = (stoppingVoltage - startingVoltage)
    scanDuration = abs ( rampInterval / scanRate )
    elapsedTime = 0.0
    Stopwatch.zeroTimer()
    while elapsedTime < scanDuration:
        elapsedTime = Stopwatch.getSinceLastZeroed()
        # manipulate the regulator setpoint:
        Vg = startingVoltage + (rampInterval / scanDuration * elapsedTime)
        Gate.set_volts(Vg)
        Gate.Measure()
        Stopwatch.Wait(loopDelay)
        Channel.Measure()
        Stopwatch.Measure()
        Data.acquireData()
    return


def Test (SDvoltages, Gvolages, SDwait, Gwait, Temperatures=None, TstabilTime=None):
    # initialization
    report ('Starting new FET measurement of I-V characteristic S-D for various Gate voltages')
    Gate.set_volts(0.0)
    Channel.set_volts(0.0)
    Gate.set_output_on()
    Channel.set_output_on()
    Stopwatch.zeroTimer()
    # detect the temperature?
    if Temperatures == None:
        roomTemp = True
    #else:
    #    roomTemp = False
    #    setpoint = Temperatures[0]  # first temp in list
    #    setTolerance = 0.2 # setpoint Temperature tolerance - absolute
    #    if TstabilTime == None:
    #        TstabilTime = 300   # 5 min for stabilisation should be enough
    #    # initialize PID temperature regulation
    #    PeltierP.set_PID_params(Kp=0.769, Ti= 44.6, Td=0.0896, looptime=0.7)
    #    PeltierP.setNew_setpoint(value=setpoint, tolerance=setTolerance, evalPeriod=TstabilTime)
    #    PeltierP.startRegulation()
    #    report ('starting Temperature Regulation: setpoint = %0.1f deg.Celsius' % setpoint)
    #    PeltierP.waitForSetpoint(2*TstabilTime)
    #    report ('Reached setpoint = %0.1f deg.Celsius' % setpoint)
  
    # Actual testing algorithm
    for Vgate in Gvolages:
        report ('applying Gate voltage = %0.3f V' % Vgate)
        Gate.set_volts(Vgate)   
        Stopwatch.Wait(Gwait)
        IVscan(SDvoltages, SDwait, roomTemp)
        Data.separateData()
    # in the case of multiple temperatures:
    
    #if not roomTemp:
    #    Temperatures = Temperatures[1:] # cut out the first temperature, which was already tested
    #    for setpoint in Temperatures:
    #        PeltierP.setNew_setpoint(value=setpoint, tolerance=setTolerance, evalPeriod=TstabilTime)
    #        report ('new temperature setpoint = %0.1f deg.Celsius' % setpoint)
    #        PeltierP.waitForSetpoint(2*TstabilTime)
    #        report ('Reached setpoint = %0.1f deg.Celsius' % setpoint)
    #        for Vgate in Gvolages:
    #            report ('applying Gate voltage = %0.3f V' % Vgate)
    #            Gate.set_volts(Vgate)   
    #            Stopwatch.Wait(Gwait)
    #            IVscan(SDvoltages, SDwait, roomTemp)
    #            Data.separateData()
        
    
    Channel.set_output_off()
    Gate.set_output_off()
    report('Experiment finished')
#end

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
    

def TransferLoop(SDvoltage, GmaxVoltage, SDwait, Grate, loopDelay=0.05):
    """ Constructs a loop of gate voltages 
    and applies them with adjustable certain voltage scan speed """
    # loopDelay = 0.05    # roughness of the regulation loop
    report ('Starting new FET dynamic transfer characteristic loop at scanrate %0.2f V/s with Max Ug = %0.1f V' % (Grate,GmaxVoltage))
    Channel.set_volts(0.0)
    Gate.set_volts(0.0)
    Gate.set_output_on()
    Channel.set_output_on()
    
    report ('applying S-D voltage = %0.3f V' % SDvoltage)
    Channel.set_volts(SDvoltage)   
    Stopwatch.Wait(SDwait)
    
    scanDuration = ( GmaxVoltage / Grate )
    # sweep gate voltage from zero to Gmax
    GateLoop(0.0, GmaxVoltage, scanDuration, Grate, loopDelay)
    Data.separateData()
    # sweep gate voltage from Gmax to -Gmax
    GateLoop(GmaxVoltage, ((-1)*GmaxVoltage), scanDuration, Grate, loopDelay)
    Data.separateData()
    # sweep gate voltage from -Gmax to zero 
    GateLoop( ((-1) * GmaxVoltage), 0.0, scanDuration, Grate, loopDelay)
    Data.separateData()
   
    #Gate.set_output_off()
    #Channel.set_output_off()
    report('Experiment finished')