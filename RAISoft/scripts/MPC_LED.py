# script for testing the modulated photocurrent using 
# External Function generator as source for photodiode

from instruments.Devices import Clock, Monochromator, LockIn, FastVoltmeter
from instruments.Devices import GeneratorSquare, Thermometer
from Output.Output import OutputHandler


# define and ACTIVATE the instruments
Stopwatch = Clock()
Stopwatch.Activate()

#PeltierP = PID_CBdriver(TCchannel=1, count=20)
#PeltierP.Activate()

Filter = Monochromator()
Filter.Activate()

LightMeter = FastVoltmeter()
LightMeter.Activate()

# The modulated photocurrent is detected by Lock In Amplifier
LI = LockIn() # The Lock In amplifier
LI.Activate()

LED = GeneratorSquare()
LED.Activate()

Temperature = Thermometer()
Temperature.Activate()

# don`t forget to activate the instruments before opening the output file:
Data = OutputHandler()
Data.setDataFileName()



def observe (duration, delay):
    Stopwatch.zeroTimer()
    while Stopwatch.getSinceLastZeroed() < duration:    # observe the temperature variables for about 5 min, wait for the Temp to stabilize
            Stopwatch.Wait(delay)
            Stopwatch.Measure()
            LI.Measure()
            Temperature.Measure()
            LED.Measure()
            Data.acquireData()



def Test(Wavelength, Voltage, VoltWait,LEDfrequencies, FreqWait, LEDamplitude,LEDoffset):
    # Initialization
    Data.report('Applied DC voltage to the sample : %d Volts' % Voltage)
    LI.set_aux_output(1, Voltage)
    Data.report('Waiting for %d seconds to stabilize' % VoltWait)
    Stopwatch.Wait(VoltWait)
    Data.report('Setting wavelength: %d nm' % Wavelength)
    Filter.set_wave(Wavelength)
    Data.report('Openning shutter' )
    Filter.open_shutter()
    Filter.Measure()
    
    #Stopwatch.Wait(1.5)
    #LockIn.set_gain(int(gain-1))
    #report ('Measuring Bias light intensity:')
    #LightMeter.Measure()
    #report ('Starting Modulated irradiation:')    
    #Filter.open_shutter()
    #Filter.Measure()
    
    # estimation of LockIn amplifier gain for desired Frequencies:
    Data.report('Measuring Light intensity at 1000 Hz (mean value) ' )
    LED.set_freq(1000)
    LED.set_amplitude_vrms(LEDamplitude)
    LED.set_offset(LEDoffset)
    LED.set_output_on()
    Stopwatch.Wait(3)
    LightMeter.Measure()
    
    Data.report ('estimation of LockIn amplifier gain for desired Frequencies:')
    
    
    Data.report ('Starting Frequency scanning:')
    for freq in LEDfrequencies:
            LED.set_freq(freq)
            Stopwatch.Wait(0.1)
            #LIfreq = LockIn.get_frequency()
            Data.report ('Set New frequency: %0.1f' % freq)
            #gain = LockIn.auto_gain()
            gain = LI.get_gain()
            Data.report('Found set Lock-In Amplifier GAIN: %d' % gain)
            minimumWait = FreqWait + 10/freq
            observe(FreqWait, 2)
            Data.separateData()
    Data.report ('Experiment finished')
