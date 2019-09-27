# This script is for testing kinetics of photocurrent during irradiation 
# 


# project libraries imports:
# instruments:
from instruments.Devices import Clock, Monochromator, Electrometer, FastVoltmeter, TemperatureRegPID_ITO


# file-output libraries
from Output.Output import OutputHandler

# define and ACTIVATE the instruments
Stopwatch = Clock()
Stopwatch.Activate()

Channel = Electrometer()
Channel.Activate()


PeltierP = TemperatureRegPID_ITO()
PeltierP.Activate()

Filter = Monochromator()
Filter.Activate()

LightMeter = FastVoltmeter()
LightMeter.Activate()

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

def observe (duration, delay=0.05):
    Stopwatch.zeroTimer()
    while Stopwatch.getSinceLastZeroed() < duration:    # observe the temperature variables for about 5 min, wait for the Temp to stabilize
            Stopwatch.Wait(delay)
            Stopwatch.Measure()
            Channel.Measure()
            LightMeter.Measure()
            PeltierP.Measure()
            Data.acquireData()
            

def Test (SDvoltage, WaitVolt, Temperatures, WaitTemp, Wavelength, timeON, timeOFF, cyclesN=1):
    # initialization
    report ('Starting new irradiation kinetics, at lambda= %d' % Wavelength)
    Filter.set_wave(Wavelength)
    Stopwatch.Wait(1)
    Filter.close_shutter()
    # stabilization of the SD current at given voltages
    
    #PeltierP.set_PID_params(Kp=2.2, Ti=20, Td=0.1, looptime=0.5)
    PeltierP.setNew_setpoint(value=Temperatures[0], tolerance=0.1, evalPeriod=60)
    PeltierP.startRegulation()
    report ('starting Temperature Regulation: setpoint = %0.1f deg.Celsius' % Temperatures[0])
    Temperatures = Temperatures[1:]
    
    report('Applying the DC voltage %f V' % SDvoltage)
    Channel.set_volts(SDvoltage)
    Channel.set_output_on()
    observe (WaitVolt)
    Data.separateData()
    
    for temperature in Temperatures:
        report('starting the the tempearture stabilization for %d seconds' % WaitTemp)
        observe (WaitTemp) # measure the stabilization of the offset current
        Data.separateData()
        PeltierP.waitForSetpoint(2*WaitTemp)
        
        #Ligth ON/OFF cycles:
        for cycle in range(cyclesN):
            report('starting the irradiation cycle No. %d' % cycle)
           
            # Start irradiating the sample
            report('starting the irradiation for %d seconds' % timeON)
            Filter.open_shutter()
            observe(timeON)
            Data.separateData()
            
            # Start the measurement in dark
            report('starting the dark kinetics for %d seconds' % timeOFF)
            Filter.close_shutter()
            observe(timeOFF)
            Data.separateData()
        
        PeltierP.setNew_setpoint(value=temperature, tolerance=0.1, evalPeriod=60)
        report ('starting Temperature Regulation: setpoint = %0.1f deg.Celsius' % temperature)
    Filter.Close()    
    report('Experiment finished')
#end
