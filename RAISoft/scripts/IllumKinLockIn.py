# This script is for testing kinetics of modulatoed photocurrent
# during irradiation by steady state BIAS light
# 

from instruments.Devices import Clock, Monochromator, Electrometer, FastVoltmeter, LockIn, Thermometer
# file-output libraries
from Output.Output import OutputHandler

# define and ACTIVATE the instruments
Stopwatch = Clock()
Stopwatch.Activate()



Filter = Monochromator()
Filter.Activate()

LightMeter = FastVoltmeter()
LightMeter.Activate()


# The modulated photocurrent is detected by Lock In Amplifier
LockInAmplifier = LockIn() # The Lock In amplifier
LockInAmplifier.Activate()

Tmeter=Thermometer()
Tmeter.Activate()

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

def observe (duration, delay=0.1):
    Stopwatch.zeroTimer()
    while Stopwatch.getSinceLastZeroed() < duration:    # observe the temperature variables for about 5 min, wait for the Temp to stabilize
            Stopwatch.Wait(delay)
            Stopwatch.Measure()
            Tmeter.Measure()
            LockInAmplifier.Measure()
            LightMeter.Measure()
            Data.acquireData()

def Test (SDvoltage, timeSTABIL, Wavelength, timeON, timeOFF, cyclesN=1):
    # initialization
    report ('Starting new irradiation kinetics, at lambda= %d' % Wavelength)
    #Filter.set_wave(Wavelength)
    #Stopwatch.Wait(1)
    Filter.close_shutter()
    LockInAmplifier.set_aux_output(1, SDvoltage)
    #Channel.set_output_on()
    #Filter.close_shutter()
    #Stopwatch.Wait(5)
    Filter.set_wave(Wavelength)
    Filter.open_shutter()
    # stabilization of the SD current at given voltages
    
    report('starting the stabilization for %d seconds' % timeSTABIL)
    #Stopwatch.zeroTimer()
    observe(timeSTABIL)
    Data.separateData()

    for cycle in range(cyclesN):
        report('starting the irradiation cycle No. %d' % cycle)
       
        # Start irradiating the sample
        report('starting the irradiation for %d seconds' % timeON)
        #Filter.close_shutter()
        #Filter.open_shutter()
        observe(timeON)
        Data.separateData()
        
        # Start the measurement in dark
        report('starting the dark kinetics for %d seconds' % timeOFF)
        Filter.close_shutter()
        #Filter.open_shutter()
        observe(timeOFF)
        Data.separateData()
    LockInAmplifier.set_aux_output(1, 0.0)
    Filter.close_shutter()
    Filter.Close()    
    report('Experiment finished')
#end


