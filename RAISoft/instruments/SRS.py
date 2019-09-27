from DummyMeter import Bedna
from numpy import array
from time import sleep


class LockInSR830(Bedna):
    def __init__(self, BUS):
        Bedna.__init__(self, BUS)
        self.Readings = {'Freq(Hz)': array([]), 
                         'MagnitudeR(VA)': array([]), 
                         'PhasePHI(deg)': array([]),
                         'MagnitudeInternal(V)': array([]),
                         'OAUX1(V)':array([]),
                         'OAUX2(V)':array([]),
                         'OAUX3(V)':array([]),
                         'OAUX4(V)':array([]),
                         'IAUX1(V)':array([]),
                         'IAUX2(V)':array([]),
                         'IAUX3(V)':array([]),
                         'IAUX4(V)':array([]) }    # define the units of the measurement readings
        self.dev.initSequence = [('OUTX 1' ), # 1 = GPIB output
                                 ('OVRM 1'), # does NOT lock up the front pannel during measurement
                                 ('SRAT 14'), # turn OFF the data storage, just single shot trigger
                                 ('FMOD 0'), #  0= use EXTERNAL reference
                                 ('RSLP 0'), # 0= synchronise on RISING edge of the external reference
                                 ('AUXV 1,0'),
                                 ('AUXV 2,0'),
                                 ('AUXV 3,0'),
                                 ('AUXV 4,0'),
                                 ]
        # some useful constants                         ] 
        self.limitI = 0.100 # limit of the source in amperes
        self.limitV = 40.0  # limit of the voltage source in volts
        self.IntRefAmplitude = 0
        self.AuxOutputs = [0.0,0.0,0.0,0.0]
        # actual parameters of the device encored in numerical values
        # see manual pages from  5-6 further
        self.frequency = 0.0 # actual measurement freq
        self.sensitivity = 1 #
        self.timeconstant = 1 #
        #self.reserve = 1 # dynamic reserve of the instrument
        self.internalRef = False # use the internal reference signal?
        self.overload = False   # is there overload on the input?
        self.finishedMeas = False   # had the previous measurement finished?
        self.init()
        self.get_frequency()
        self.get_gain()
        self.get_time_constant()
        return
    def get_gain(self,timeout=None):
        self.Bus.write_string('SENS?')
        reading = self.Bus.read_values(timeout)
        self.sensitivity = reading[0]
        return self.sensitivity
    def set_gain(self,gain,timeout=None):
        self.Bus.write_string('SENS %d' % gain,timeout)
        return
    def auto_gain(self):
        self.Bus.write_string('AGAN')
        InterfaceReady = 2
#        while not ( self.Bus.read_stb()  & InterfaceReady):
#            pass
        #self.Bus.write_string('AGAN')
        gain = self.get_gain(timeout=99)
        return gain
    def get_time_constant(self):
        self.Bus.write_string('OFLT?')
        reading = self.Bus.read_values()
        self.timeconstant = reading[0]
        return self.timeconstant
    def set_time_constant(time,self):
        self.Bus.write_string('OFLT %d' % time)
        return
    def get_frequency(self):
        self.Bus.write_string('FREQ?')
        reading = self.Bus.read_values()
        self.frequency = reading[0]
        return self.frequency
    def get_measurement(self):
        """This function reads the measured values 3=R and 4=phase"""
        self.Bus.write_string('SNAP? 3,4,9,5,6,7',timeout=1.0)
        #self.Timer.Wait(0.1)
        reading = self.Bus.read_floats(timeout=1.0, separators=',')
        if not (len(reading) == 6):
            reading = (0.0,0.0,0.0,0.0,0.0,0.0)
        return reading
    def get_overload(self):
        self.Bus.write_string('LIAS? 0')
        reading = self.Bus.read_values()
        self.sensitivity = reading[0]
        if reading[0]:
            self.overload = True
        else:
            self.overload = False
        return self.overload
    def set_internal_reference_on(self):
        self.Bus.write_string('FMOD 1')
        self.internalRef = True
    def set_internal_reference_off(self):
        self.Bus.write_string('FMOD 0')
        self.internalRef = False
    def set_frequency(self, frequency):
        if self.internalRef:
            self.Bus.write_string('FREQ %f' % frequency)
        else:
            pass
        return
    def set_sine_amplitude(self, amplitude):
        amplitude = abs(amplitude)
        if amplitude > 10.5:
            amplitude = 10.5
        if self.internalRef:
            self.Bus.write_string('SLVL %f' % amplitude)
            self.IntRefAmplitude = amplitude
        else:
            pass
        return
    def get_sine_amplitude(self):
        if self.internalRef:
            amplitude = self.Bus.ask_for_values('SLVL?')
            response = amplitude[0]
        else:
            response = 0
        return response
    def set_aux_output(self,channel, voltage):
        """ sets one of the specified auxiliary output to voltage level """
        # get in correct range 
        if voltage > 10.5:
            voltage = 10.5
        if voltage < -10.5:
            voltage = -10.5
        if channel in range(1,5):
            self.Bus.write_string('AUXV %(chan)d,%(voltage)6.3f' %  {'chan':channel, 'voltage':voltage} )
            self.AuxOutputs[channel-1]=voltage
        return
    def get_aux_output(self,channel):
        """ sets one of the specified auxiliary output to voltage level """
        # get in correct range 
        if channel in range(1,5):
            response = self.Bus.ask_for_values('AUXV? %(chan)d' %  {'chan':channel,})
            voltage = response[0]
        return voltage
    def get_aux_input(self,channel):
        """ sets one of the specified auxiliary output to voltage level """
        # get in correct range 
        if channel in range(1,5):
            response = self.Bus.ask_for_values('OAUX? %(chan)d' %  {'chan':channel,})
            voltage = response[0]
        return voltage
    def Measure(self):
        reading = self.get_measurement()
        #self.frequency = self.get_frequency()
        self.Readings['Freq(Hz)'] = array([reading[2]])
        self.Readings['MagnitudeR(VA)'] = array([reading[0]])
        self.Readings['PhasePHI(deg)'] = array([reading[1]])
        self.Readings['IAUX1(V)'] = array([reading[3]])
        self.Readings['IAUX2(V)'] = array([reading[4]])
        self.Readings['IAUX3(V)'] = array([reading[5]])
        # this one cannot be read from instrument
        self.Readings['IAUX4(V)'] = array([0.0])
        self.Readings[ 'MagnitudeInternal(V)'] = array([self.IntRefAmplitude])
        for channel in range (1,5):
            parameterName = 'OAUX%d(V)' % channel
            self.Readings[ parameterName ] = array([self.AuxOutputs[channel-1]])
        measurement_error = 0
        return measurement_error

    
