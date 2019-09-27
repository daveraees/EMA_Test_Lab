# project libraries imports:
# instruments:
from GenericScript import TestScript

    
class Test(TestScript):
    def __init__(self):
        TestScript.__init__(self)
        self.Name = 'Current-Voltage'
        self.Description = """Current Voltage characteristic measurement"""
        return
    def init_parameters(self):
        """
        create the list of the parameter and initialize some basic values
        """
        #voltages, acquizDelay=0.1, voltStepDelay=5
        self.generate_parameter(Name='Tungsten lamp voltage',
                                Unit='Volts', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ 20, 0.0, None], 
                                Description='Select value > 0 to activate irradiation of the sample with light')
        self.set_parameter_value('Tungsten lamp voltage', 0.0)
        
        self.generate_parameter(Name='Tested wavelength', 
                                Unit='nm',
                                Type='float', 
                                Iterable = False,
                                Limits = [ 1200, 200, None], 
                                Description='List of wavelengths to irradiate the sample with, in the given order')
        self.set_parameter_value('Tested wavelength', 800)
        
        self.generate_parameter(Name='Tested voltages', 
                                Unit='Volts',
                                Type='float', 
                                Iterable = True,
                                Limits = [ 1000, -1000, None], 
                                Description='List of voltages (in Volts) to be applied to the sample given order')
        #self.set_parameter_value('Tested voltages', [0.1,0.2])
        self.generate_parameter(Name='Acquisition delay',
                                Unit='Seconds', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ None, None, [0.01, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]], 
                                Description='delay of the data acquizition loop in seconds')
        self.set_parameter_value('Acquisition delay', 0.1)
        self.generate_parameter(Name='Acquisition time',
                                Unit='Seconds', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ None, 0.001, None], 
                                Description='delay between the voltage steps in seconds')
        self.set_parameter_value('Acquisition time', 5.0)
        self.generate_parameter(Name='Device',
                                Unit='name', 
                                Type='name', 
                                Iterable = False, 
                                Limits = [ None, None, ['Keithley 617','Keithley 6517A (A)','Keithley 6517A (B)','Keithley 2602 - channel A','Keithley 2602 - channel A, fast sweep','Keithley 2602 - channel B','Keithley 2602 - channel B, fast sweep','TTi TSX3510P']], 
                                Description='Device to measure the current voltage characteristics with')
        self.set_parameter_value('Device', 'Keithley 617')
        self.generate_parameter(Name='Thermo',
                                Unit='name', 
                                Type='name', 
                                Iterable = False, 
                                Limits = [ None, None, ["HAAKE F6", "none"]], 
                                Description='Device to measure the temperature with')
        self.set_parameter_value('Thermo', 'none')
        return
    def init_devices(self):
        from Devices import Clock, Thermometer                            
        
        self.deviceName = self.get_parameter_value('Device')
        
        LampVoltage = self.get_parameter_value('Tungsten lamp voltage')
        if LampVoltage > 0:
            from Devices import PowerSource, Monochromator, HamamatsuPhotodiode
            self.Filter = Monochromator()
            self.append_active_devices_list(self.Filter)
            self.LightMeter = HamamatsuPhotodiode()
            self.append_active_devices_list(self.LightMeter)
            if self.deviceName != 'TTi TSX3510P':
                self.Lamp = PowerSource()
                self.Lamp.set_amperes_limit(10.0)
        
        if self.deviceName == 'Keithley 6517A (A)':
            from Devices import ElectrometerA
            self.Elmeter = ElectrometerA()
            self.append_active_devices_list(self.Elmeter)
        if self.deviceName == 'Keithley 6517A (B)':
            from Devices import ElectrometerB
            self.Elmeter = ElectrometerB()
            self.append_active_devices_list(self.Elmeter)
        
        if self.deviceName == 'Keithley 617':
            from Devices import Electrometer
            self.Elmeter = Electrometer()
            self.append_active_devices_list(self.Elmeter)
        if self.deviceName == 'TTi TSX3510P':
            from Devices import PowerSource
            self.Elmeter = PowerSource()
            self.Elmeter.set_amperes_limit(10.0)
            self.append_active_devices_list(self.Elmeter)
        if self.deviceName == 'Keithley 2602 - channel A':
            from Devices import SMU_channelA
            self.Elmeter = SMU_channelA()
            self.append_active_devices_list(self.Elmeter)
        if self.deviceName == 'Keithley 2602 - channel B':
            from Devices import SMU_channelB
            self.Elmeter = SMU_channelB()
            self.append_active_devices_list(self.Elmeter)
        if self.deviceName == 'Keithley 2602 - channel A, fast sweep':
            from Devices import SMU_channelA
            self.Elmeter = SMU_channelA()
            self.append_active_devices_list(self.Elmeter)
        if self.deviceName == 'Keithley 2602 - channel B, fast sweep':
            from Devices import SMU_channelB
            self.Elmeter = SMU_channelB()
            self.append_active_devices_list(self.Elmeter)
        #from instruments.Keithley import Electrometer617
        #from instruments.Agilent import A34401_4ohm
        ################################################################
        ##  Here begins the initialization of devices ##################
        ################################################################
        # define and ACTIVATE the instruments
        self.Stopwatch = Clock()
        self.append_active_devices_list(self.Stopwatch)
        if self.get_parameter_value('Thermo') == "HAAKE F6":            
            self.Temper = Thermometer()
            self.append_active_devices_list(self.Temper)
    def _run(self):
        """ simple current-voltage characteristics measurement """
        ################################################################
        ##  Here begins the experimetal part ###########################
        ################################################################
        
        # switch on the voltage source:
        
        voltages = self.get_parameter_value('Tested voltages')
        voltStepDelay = self.get_parameter_value('Acquisition time')
        acquizDelay = self.get_parameter_value('Acquisition delay')
        
        LampVoltage = self.get_parameter_value('Tungsten lamp voltage')
        Wavelength = self.get_parameter_value('Tested wavelength')
        
        if LampVoltage > 0:
            #self.LightMeter.Measure()
            if self.deviceName != 'TTi TSX3510P':
                self.Lamp.set_volts(LampVoltage)
                self.Lamp.set_output_on()
            self.Filter.set_wave(Wavelength)
            self.Filter.open_shutter()
            if self.deviceName in ['Keithley 617']:
                self.Elmeter.zero_check('off')
            self.observe(voltStepDelay, acquizDelay)
            self.datastore.separateData()
        
        if self.deviceName in ['Keithley 617','Keithley 6517A (A)','Keithley 6517A (B)']:
            self.Elmeter.set_output_on()
            self.Elmeter.zero_check('off')
            for voltage in voltages:
                self.Elmeter.set_volts(voltage)
                self.observe(voltStepDelay, acquizDelay)
                #self.datastore.separateData()
            self.Elmeter.zero_check('on')
            self.Elmeter.set_output_off()
        
        if self.deviceName in ['TTi TSX3510P','Keithley 2602 - channel A','Keithley 2602 - channel B']:
            self.Elmeter.set_output_on()
            for voltage in voltages:
                self.Elmeter.set_volts(voltage)
                self.observe(voltStepDelay, acquizDelay)
                self.datastore.separateData()
            self.Elmeter.set_output_off()
        
        if self.deviceName in ['Keithley 2602 - channel A, fast sweep',
                               'Keithley 2602 - channel B, fast sweep']:
            numberOfPoints = len(voltages)
            self.Temper.Measure()
            self.Stopwatch.Measure()
            self.Elmeter.MeasureIListV(voltages, settle_time=voltStepDelay)
            self.datastore.acquireData()
            


from AllScripts import ScriptsBase
ScriptsBase.add_script(Test, 'Simple')
