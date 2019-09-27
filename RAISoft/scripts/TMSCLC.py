"""
this is script meant perform: Experiemtstemperature-modulated space-charge limited currents
"""

# project libraries imports:
# instruments:
from instruments.TimeMeter import MainTimerClass
from instruments.Keithley import Electrometer6517
from instruments.PID import PIDHeater
from instruments.Agilent import A34401_4ohm

# file-output libraries
from Output.Output import OutputHandler

# define and ACTIVATE the instruments
Stopwatch = MainTimerClass()
Stopwatch.Activate()
#Electrometer = Electrometer617('Electrometer')
#Electrometer.Activate()
Electrometer = Electrometer6517('Electrometer')
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
import time
from numpy import linspace

def observe (duration, delay=0.5):
    """general repeating data acquizition cycle"""
    Stopwatch.zeroTimer()
    while Stopwatch.getSinceLastZeroed() < duration:    # observe the temperature variables for about 5 min, wait for the Temp to stabilize
            Stopwatch.Wait(delay)
            Stopwatch.Measure()
            Electrometer.Measure()
            Platinum.Measure()
            PeltierP.Measure()
            Data.acquireData()

def careful_voltage(voltage, stepNumber, delay):
    """divides the voltage step in number of smaller ones linearly"""
    actualV = Electrometer.get_volts()
    smoothedSteps = linspace(actualV, voltage, stepNumber)
    for volt in smoothedSteps:
        Electrometer.set_volts(volt)
        Stopwatch.Wait(delay)

import time
def report(message, file='report.info'):
    date = time.asctime(time.localtime())
    message = ('%(date)s: %(message)s \n' % \
            {'date':date, 'message':message})
    print message,
    f = open(file, 'a')
    f.write(message)
    f.close()

def Test(voltages, voltStabTime, Temp):
    
    rampStep = Temp['rampStep']       # the height of ramp in degrees of Celsius
    rampTime = Temp['rampTime']      # time of ramp in seconds
    setpoint = Temp['setpoint']      # base temperature of the ramping steps
    setTolerance = Temp['setTolerance']      # setpoint evaluation tolerance +- absolute error in deg.C
    evalTime = Temp['evalTime']      # setpoint evaluation time in seconds
    setpointTimeout = Temp['setpointTimeout']      # timeout for waiting for setpoint in seconds
    
    # switch on the voltage source:
    report ('starting new TMSCLCS experiment run NOW! - applying 0.0 V to the sample')
    Electrometer.set_volts(0.0) 
    Electrometer.set_output_on()
    
    # initialize PID temperature regulation
    PeltierP.set_PID_params(Kp=-1.788, Ti=12.8, Td=0.313, looptime=0.1)
    PeltierP.setNew_setpoint(value=setpoint, tolerance=setTolerance, evalPeriod=evalTime)
    PeltierP.startRegulation()
    report ('starting Temperature Regulation: setpoint = %0.1f deg.Celsius' % setpoint)
    observe (duration=voltStabTime, delay=0.5) # measure the stabilization of the offset current
    Data.separateData()
    PeltierP.waitForSetpoint(2*setpointTimeout)
    
    # adjust the temperature slope for future cycles
    finalPower = Data.analysis.average_last('U(V)',100) # calculate the mean of the voltage needed to reach the setpoint
    report ('Calculated average voltage at Peltier  %.3f V' % finalPower)
    
    Data.analysis.mark_from()
    PeltierP.linRamp(difference=(rampStep)/2.0, duration=rampTime/2.0)
    observe (duration=rampTime/2.0, delay=0.5)
    Data.analysis.mark_to()
    Data.separateData()
    # intercept and slope are the parameters of thre regressed line, first_coordinate is the power calcualted at the beginning of the ramp
    # r, tt, stderr are the statistical parameters of the fit 
    (intercept, slope, first_coordinate, r, tt, stderr) = Data.analysis.linear_regres_marked("time(s)", "U(V)")
    report('parameters of the temperature ramp: intercept=%.4f slope=%e, std error= %e' % (intercept,slope,stderr))
    PeltierP.setNew_setpoint(value=setpoint, tolerance=setTolerance, evalPeriod=evalTime)
    PeltierP.waitForSetpoint(setpointTimeout)
    #start ramping the temperature
    for voltage in voltages:
        #Electrometer.set_volts(voltage) # set next voltage step
        report ('appling new voltage: %0.3f V to the sample' % voltage)
        careful_voltage(voltage, 5, 1.5)    # voltage is negative because of the experimental setup. It results in positive at ITO
        stabilization = voltStabTime-20
        report ('stabilization at new voltage: %d seconds begins NOW' % stabilization)
        observe (duration=stabilization, delay=0.5) # measure
        PeltierP.regulate(False)
        report('Peltier Close loop PID regulation paused')
        poweroutput = Data.analysis.average_last('U(V)',30)
        PeltierP.valve.set_volts(poweroutput)
        report('Applying stable voltage %.3f V to the Peltier' %  poweroutput)
        Data.analysis.mark_from()
        observe (duration=20, delay=0.5) # measure stabilized current for a while without Peltier regulation
        Data.analysis.mark_to()
        meanCurrent = Data.analysis.average_marked('Curr6517(A)')
        report('Stabilized values: current = %e A at voltage %0.3f V at base temperature %.2f deg.Celsius' \
               %  (meanCurrent, voltage, setpoint) )
        Data.separateData()
        report ('starting temperature ramp')
        Data.analysis.mark_from()
        Stopwatch.zeroTimer()
        while Stopwatch.getSinceLastZeroed() < rampTime:    # observe the temperature variables for about 5 min, wait for the Temp to stabilize
                Stopwatch.Wait(0.5)
                Stopwatch.Measure()
                Electrometer.Measure()
                PeltierP.sensor.Measure()
                PeltierP.Measure()
                Platinum.Measure()
                Data.acquireData()
                moment = Stopwatch.getSinceLastZeroed()
                if (moment % 10 ) > 9:                 # every about 10 sec adjust votlage of Peltier power output
                   poweroutput = first_coordinate[1] + (moment * slope)
                   PeltierP.valve.set_volts(poweroutput)
                   PeltierP.valve.Measure()
        Data.analysis.mark_to()
        Data.separateData()
        report ('temperature ramp finished')
        (energy,zeroKcurrent,r,tt,stderr) = Data.analysis.AE_marked('Temp(degC)', 'Curr6517(A)')
        report ('Calculated values from the ramp:\n voltage=%.2f V, Activation energy=%.3f eV, current at 0K = %e A, std error= %e' \
                % (voltage, energy, zeroKcurrent, stderr))
        PeltierP.regulate(True)
        PeltierP.setNew_setpoint(value=setpoint, tolerance=setTolerance, evalPeriod=evalTime)
        observe (duration=150, delay=0.5)
        Data.separateData()
        PeltierP.waitForSetpoint(setpointTimeout)
    
    Data.separateData()
    report ('all voltages tested. experiment almost finished')
    PeltierP.setNew_setpoint(value=setpoint, tolerance=setTolerance, evalPeriod=evalTime)
    
    observe (duration=150, delay=0.5) # observe the temperature variables for about 5 min, wait for the Temp to stabilize
    
    #Electrometer.set_output_off()