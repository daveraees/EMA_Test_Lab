# project libraries imports:
# instruments:
from GenericScript import TestScript

class Test(TestScript):
    def __init__(self):
        TestScript.__init__(self)
        self.Name = 'Modulated photocurrent frequency spectrum'
        self.Description = """Measurement of the modulation frequency spectrum of photocurrent"""
        return
    def init_parameters(self):
        """
        create the list of the parameter and initialize some basic values
        """
        #voltages, acquizDelay=0.1, voltStepDelay=5
        self.generate_parameter(Name='Tested wavelength', 
                                Unit='nm',
                                Type='float', 
                                Iterable = False,
                                Limits = [ 1200, 200, None], 
                                Description='Wavelengths to irradiate the sample with')
        self.set_parameter_value('Tested wavelength', 800)
        
        self.generate_parameter(Name='Tested frequencies', 
                                Unit='Hz',
                                Type='float', 
                                Iterable = True,
                                Limits = [ 1e5, 0.01, None], 
                                Description='Light chopper modulation frequencies')
        #self.set_parameter_value('Tested frequencies', 64)
        
        self.generate_parameter(Name='Lamp voltage',
                                Unit='Volts', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ 20, 0.0, None], 
                                Description='Voltage to be applied to the light source (Tungsten Lamp, or LED)')
        self.set_parameter_value('Lamp voltage', 20.0)
        
        self.generate_parameter(Name='Lamp voltage offset',
                                Unit='Volts', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ 5, 0.0, None], 
                                Description='Offset voltage to be applied to the LED light source in case of Agilent Waveform generator is used')
        self.set_parameter_value('Lamp voltage offset', 0.0)
        
        self.generate_parameter(Name='Acquisition delay',
                                Unit='Seconds', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ None, None, [0.01, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]], 
                                Description='delay of the data acquizition loop in seconds')
        self.set_parameter_value('Acquisition delay', 2.0)
        
        self.generate_parameter(Name='Settle time frequency',
                                Unit='Seconds', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ None, 0.001, None], 
                                Description='Delay to settle signal at each frequency in seconds')
        self.set_parameter_value('Settle time frequency', 5.0)
        
        self.generate_parameter(Name='Settle time DC volts',
                                Unit='Seconds', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ None, 0.001, None], 
                                Description='Delay before the irradiation starts, with applied voltage to settle the current (in seconds)')
        self.set_parameter_value('Settle time DC volts', 5.0)
        
        self.generate_parameter(Name='DC voltage',
                                Unit='Volts', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ 10.5, -10.5, None], 
                                Description='DC voltage to be applied to the sample from AUX OUT 1 of the LockIn Apmlifier')
        self.set_parameter_value('DC voltage', 0.0)
        
        self.generate_parameter(Name='Chopper device',
                                Unit='', 
                                Type='name', 
                                Iterable = False, 
                                Limits = [ None, None, ['Wheel chopper SR530','Agilent 33220A Waveform generator']], 
                                Description="""Device to provide modulation of irradiation. 
                                In case of Wheel chopper, the wavelength will be adjusted by monochromator 
                                and chopper frequency will be adjusted by LockIn AUX OUT 2 (0.6 - 10.5 V)
                                connected to the control voltage input of the wheel controler.
                                
                                In case of Agilent 33220A Waveform generator, the set frequencies will be selected
                                on the output terminal of the device, e.g. to feed LED""")
        self.set_parameter_value('Chopper device', 'Wheel chopper SR530')
        return
    def init_devices(self):
        from Devices import Clock, Thermometer, PowerSource,\
                            Monochromator, LockIn,\
                            HamamatsuPhotodiode, GeneratorSquare
                            
        
        self.Channel = LockIn()
        self.append_active_devices_list(self.Channel)
        
        deviceName = self.get_parameter_value('Chopper device')
        if deviceName == 'Wheel chopper SR530':
            self.Filter = Monochromator()
            self.append_active_devices_list(self.Filter)
            self.Lamp = PowerSource()
            self.append_active_devices_list(self.Lamp)
        if deviceName == 'Agilent 33220A Waveform generator':
            self.Filter = Monochromator()
            self.append_active_devices_list(self.Filter)
            self.Chopper = GeneratorSquare()
            self.append_active_devices_list(self.Chopper)
        #from instruments.Keithley import Electrometer617
        #from instruments.Agilent import A34401_4ohm
        ################################################################
        ##  Here begins the initialization of devices ##################
        ################################################################
        # define and ACTIVATE the instruments
        
        #PeltierP = PID_CBdriver(TCchannel=1, count=20)
        #PeltierP.Activate()

        self.LightMeter = HamamatsuPhotodiode()
        self.append_active_devices_list(self.LightMeter)
        self.Stopwatch = Clock()
        self.append_active_devices_list(self.Stopwatch)
        self.Temper = Thermometer()
        self.append_active_devices_list(self.Temper)
    def _run(self):
        """ simple current-voltage characteristics measurement """
        ################################################################
        ##  Here begins the experimetal part ###########################
        ################################################################
        
        deviceName = self.get_parameter_value('Chopper device')
        Wavelength = self.get_parameter_value('Tested wavelength')
        Frequencies = self.get_parameter_value('Tested frequencies')
        DCvoltage = self.get_parameter_value('DC voltage')
        LampVolt = self.get_parameter_value('Lamp voltage')
        LampOffset = self.get_parameter_value('Lamp voltage offset')
        WaitDC = self.get_parameter_value('Settle time DC volts')
        WaitWL = self.get_parameter_value('Settle time frequency')
        WaitDAQ = self.get_parameter_value('Acquisition delay')
        # parameters for recalcualtion of the frequencies to the voltages:
        WheelChopperVoltageCoeff = 0.005 
        WheelChopperVoltageOffset = 0.0
        
        self.datastore.report('Using device "%(device)s" for modulation'  % \
            {'device':deviceName})
        
        # initializing the measurement for given instrument:
        if deviceName == 'Wheel chopper SR530':
            self.Filter.close_shutter()
            self.Filter.set_wave(Wavelength)
            self.Lamp.set_volts(LampVolt)
            self.Lamp.set_amperes_limit(10)
            self.Lamp.set_output_on()
            # calculate the voltages set to regulate frequencies
            self.Channel.set_aux_output(2, 1.0)
            self.Filter.open_shutter()
            self.Stopwatch.Wait(3)
            
        # initializing the measurement for given instrument:
        if deviceName == 'Agilent 33220A Waveform generator':
            self.Filter.close_shutter()
            self.Filter.set_wave(Wavelength)
            self.Chopper.set_duty_cycle(50)
            self.Chopper.set_freq(1000)
            LEDamplitude = LampVolt - LampOffset
            LEDoffset = LampOffset
            self.Chopper.set_amplitude_vrms(LEDamplitude)
            self.Chopper.set_offset(LEDoffset)
            self.Chopper.set_output_on()
            self.Filter.open_shutter()
            self.Stopwatch.Wait(3)
        
        # apply DC voltage to the sample and
        # measure during 1kHz irradiation
        self.datastore.report('Stabilizing the DC voltage at the sample, irradiation modulation at 1 kHz' )
        self.Channel.set_aux_output(channel=1, voltage=DCvoltage)
        self.datastore.report('Irradiation wavelength %0.1f nm' % Wavelength )
        self.observe(WaitDC,WaitDAQ)
                
        #self.datastore.report ('estimation of LockIn amplifier gain for desired Frequencies:')
    
        self.datastore.report('Starting the modulated photocurrent spectra measurement from %(from)f to %(to)f Hz'  % \
            {'from':Frequencies[0], 'to':Frequencies[-1]})
        self.datastore.report ('Starting Frequency scanning:')
        for freq in Frequencies:
            if deviceName == 'Wheel chopper SR530':
                ChopperVoltage = freq * WheelChopperVoltageCoeff + WheelChopperVoltageOffset
                self.Channel.set_aux_output(channel=2, voltage=ChopperVoltage)
            if deviceName == 'Agilent 33220A Waveform generator':
                self.Chopper.set_freq(freq) 
                self.Stopwatch.Wait(0.1)
            self.datastore.report ('Set New frequency: %0.1f' % freq)
            if freq > 9.99:
                gain = self.Channel.auto_gain()
                self.datastore.report('Found new Lock-In Amplifier GAIN: %d' % gain)
            
            else:
                gain = self.Channel.get_gain()
                self.datastore.report('Kept old Lock-In Amplifier GAIN: %d' % gain)
            minimumWait = WaitWL + 10/freq
            self.observe(WaitWL, WaitDAQ)
            self.datastore.separateData()
            
        self.datastore.report ('Experiment finished')
        
        self.Channel.set_aux_output(channel=1, voltage=0.0)
        
        if deviceName == 'Wheel chopper SR530':
            #self.Lamp.set_output_off()
            #self.Filter.close_shutter()
            self.Channel.set_aux_output(channel=2, voltage=1.0)
        
        if deviceName == 'Agilent 33220A Waveform generator':
            #self.Chopper.set_output_off()
            pass
        
        #self.datastore.report('finished the Modulated frequency photocurrent spectrum measurement')
        return

from AllScripts import ScriptsBase
ScriptsBase.add_script(Test, 'Photoconductivity')