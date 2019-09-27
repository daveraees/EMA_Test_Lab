# project libraries imports:
# instruments:
from GenericScript import TestScript

class Test(TestScript):
    def __init__(self):
        TestScript.__init__(self)
        self.Name = 'Photocurrent spectrum'
        self.Description = """Measurement of the spectrum of photoconductivity"""
        return
    def init_parameters(self):
        """
        create the list of the parameter and initialize some basic values
        """
        #voltages, acquizDelay=0.1, voltStepDelay=5
        self.generate_parameter(Name='Tested wavelengths', 
                                Unit='nm',
                                Type='float', 
                                Iterable = True,
                                Limits = [ 1200, 200, None], 
                                Description='List of wavelengths to irradiate the sample with, in the given order')
        #self.set_parameter_value('Tested wavelengths', [750])
        
        self.generate_parameter(Name='Tungsten lamp voltage',
                                Unit='Volts', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ 20, 0.0, None], 
                                Description='Select value > 0 to activate irradiation of the sample with light')
        self.set_parameter_value('Tungsten lamp voltage', 20.0)
        
        self.generate_parameter(Name='Acquisition delay',
                                Unit='Seconds', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ None, None, [0.01, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]], 
                                Description='delay of the data acquizition loop in seconds')
        self.set_parameter_value('Acquisition delay', 0.1)
        
        self.generate_parameter(Name='Settle time irradiated',
                                Unit='Seconds', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ None, 0.001, None], 
                                Description='Delay between the wavelength steps in seconds')
        self.set_parameter_value('Settle time irradiated', 5.0)
        
        self.generate_parameter(Name='Settle time in dark',
                                Unit='Seconds', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ None, 0.001, None], 
                                Description='Delay before the irradiation starts, with applied voltage to settle the dark current (in seconds)')
        self.set_parameter_value('Settle time in dark', 5.0)
        
        self.generate_parameter(Name='DC voltage',
                                Unit='Volts', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ 100, -100, None], 
                                Description='DC voltage to be applied to the sample')
        self.set_parameter_value('DC voltage', 0.0)
        
        self.generate_parameter(Name='Device',
                                Unit='', 
                                Type='name', 
                                Iterable = False, 
                                Limits = [ None, None, ['Keithley 617','Keithley 2602 - channel A','Keithley 2602 - channel B','SR830 Lock In Amplifier']], 
                                Description='Device to measure the photocurrent with characteristics\n In case of measurement with Lock In apmlifier, the AUX output 1 is used to apply the DC voltage (range -10 - +10 V)')
        self.set_parameter_value('Device', 'Keithley 617')
        return
    def init_devices(self):
        from Devices import Electrometer, Clock, Thermometer, PowerSource,\
                            SMU_channelA, SMU_channelB, Monochromator, LockIn,\
                            HamamatsuPhotodiode
        
        deviceName = self.get_parameter_value('Device')
        if deviceName == 'Keithley 617':
            self.Channel = Electrometer()
            self.append_active_devices_list(self.Channel)
        if deviceName == 'SR830 Lock In Amplifier':
            self.Channel = LockIn()
            self.append_active_devices_list(self.Channel)
        if deviceName == 'Keithley 2602 - channel A':
            self.Channel = SMU_channelA()
            self.append_active_devices_list(self.Channel)
        if deviceName == 'Keithley 2602 - channel B':
            self.Channel = SMU_channelB()
            self.append_active_devices_list(self.Channel)
        #from instruments.Keithley import Electrometer617
        #from instruments.Agilent import A34401_4ohm
        ################################################################
        ##  Here begins the initialization of devices ##################
        ################################################################
        # define and ACTIVATE the instruments
        
        #PeltierP = PID_CBdriver(TCchannel=1, count=20)
        #PeltierP.Activate()

        self.Filter = Monochromator()
        self.append_active_devices_list(self.Filter)
        self.LightMeter = HamamatsuPhotodiode()
        self.append_active_devices_list(self.LightMeter)
        self.Lamp = PowerSource()
        self.append_active_devices_list(self.Lamp)
        self.Stopwatch = Clock()
        self.append_active_devices_list(self.Stopwatch)
        self.Temper = Thermometer()
        self.append_active_devices_list(self.Temper)
    def _run(self):
        """ simple current-voltage characteristics measurement """
        ################################################################
        ##  Here begins the experimetal part ###########################
        ################################################################
        
        deviceName = self.get_parameter_value('Device')
        Wavelengths = self.get_parameter_value('Tested wavelengths')
        DCvoltage = self.get_parameter_value('DC voltage')
        LampVolt = self.get_parameter_value('Tungsten lamp voltage')
        WaitDC = self.get_parameter_value('Settle time in dark')
        WaitWL = self.get_parameter_value('Settle time irradiated')
        WaitDAQ = self.get_parameter_value('Acquisition delay')
        
        self.datastore.report('starting the photocurrent spectra measurement from %(from)d to %(to)d nm'  % \
            {'from':Wavelengths[0], 'to':Wavelengths[-1]})
        self.datastore.report('Using device "%(device)s" to measure the current'  % \
            {'device':deviceName})
        
        
        self.Filter.close_shutter()
        self.Lamp.set_volts(LampVolt)
        self.Lamp.set_amperes_limit(10)
        self.Lamp.set_output_on()
        
        deviceName = self.get_parameter_value('Device')
        # initializing the measurement for given instrument:
        if deviceName == 'Keithley 617':
            self.Channel.set_volts(DCvoltage)
            self.Channel.set_output_on()
            self.Channel.zero_check('off')
        
        if deviceName == 'SR830 Lock In Amplifier':
            self.Channel.set_aux_output(1, DCvoltage)
            pass
        
        if deviceName in ['Keithley 2602 - channel A','Keithley 2602 - channel B']:
            self.Channel.set_volts(DCvoltage)
            self.Channel.set_output_on()
            pass
        
            
        
        self.observe(WaitDC,WaitDAQ)
        
        # start the irradiation
        self.Filter.open_shutter()
    
        for wl in Wavelengths:
            self.Filter.set_wave(wl)
            self.Filter.Measure()
            self.observe(WaitWL,WaitDAQ)
            self.datastore.separateData()
        
        if deviceName == 'Keithley 617':
            self.Channel.set_output_off()
            self.Channel.zero_check('on')
        
        if deviceName == 'SR830 Lock In Amplifier':
            self.Channel.set_aux_output(1, 0.0)
            pass
        
        if deviceName in ['Keithley 2602 - channel A','Keithley 2602 - channel B']:
            self.Channel.set_output_off()
            pass
        
        self.Lamp.set_output_off()
        self.Filter.close_shutter()
        self.datastore.report('finished the photocurrent spectrum measurement')
        return


from AllScripts import ScriptsBase
ScriptsBase.add_script(Test, 'Simple')