# project libraries imports:
# instruments:
from GenericScript import TestScript

    
class Test(TestScript):
    def __init__(self):
        TestScript.__init__(self)
        self.Name = 'Mott-Schottky characteristics'
        self.Description = """Measurement of the DC bias voltage dependence of the device capacitance.\n
        Using devices:
        - SR830 Lock In amplifier for current measurement 
        - Agilent Waveform generator for applying a superposition of AC harmonic voltage signal and DC bias
        
        It can perform DC bias scans for given frequency
        """
        
        return
    def init_parameters(self):
        """
        create the list of the parameter and initialize some basic values
        """
        #voltages, acquizDelay=0.1, voltStepDelay=5
        
        
        self.generate_parameter(Name='Probing frequency', 
                                Unit='Hz',
                                Type='float', 
                                Iterable = False,
                                Limits = [ 1e3, 1e-1, None], 
                                Description='Frequencies (in Hz) to probe the AC capacitance with.')
        self.set_parameter_value('Probing frequency', 1e3)
        
        self.generate_parameter(Name='DC bias voltages', 
                                Unit='Volts',
                                Type='float', 
                                Iterable = True,
                                Limits = [ 4.5, -4.5, None], 
                                Description='List of frequencies (in Volts) to probe the AC capacitance')
        
        self.generate_parameter(Name='AC probing signal', 
                                Unit='Volts, RMS',
                                Type='float', 
                                Iterable = False,
                                Limits = [ 0.35, -0.35, None], 
                                Description='List of frequencies (in Volts) to probe the AC capacitance')
        self.set_parameter_value('AC probing signal',0.1)
        
        self.generate_parameter(Name='Settle time frequency',
                                Unit='Seconds', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ None, 0.001, None], 
                                Description='delay after applying given frequency, in seconds')
        self.set_parameter_value('Settle time frequency', 5.0)
        
        self.generate_parameter(Name='Settle time DC bias',
                                Unit='Seconds', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ None, 0.001, None], 
                                Description='delay after applying given DC voltage, in seconds')
        self.set_parameter_value('Settle time DC bias', 5.0)
        
        self.generate_parameter(Name='Acquisition delay',
                                Unit='Seconds', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ None, None, [0.01, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]], 
                                Description='delay of the data acquizition loop in seconds')
        self.set_parameter_value('Acquisition delay', 0.1)
        
        return
    def init_devices(self):
        from Devices import Clock, Thermometer, LCR_LockIn_Agilent
       
        ################################################################
        ##  Here begins the initialization of devices ##################
        ################################################################
        # define and ACTIVATE the instruments
        
        self.LCR = LCR_LockIn_Agilent()
        self.append_active_devices_list(self.LCR)
        self.Stopwatch = Clock()
        self.append_active_devices_list(self.Stopwatch)
        self.Temper = Thermometer()
        self.append_active_devices_list(self.Temper)
    def _run(self):
        """ simple current-voltage characteristics measurement """
        ################################################################
        ##  Here begins the experimetal part ###########################
        ################################################################
        
        # switch on the voltage source:
        
        DCvoltages = self.get_parameter_value('DC bias voltages')
        DCwait = self.get_parameter_value('Settle time DC bias')
        ACvoltage = self.get_parameter_value('AC probing signal')
        Freq = self.get_parameter_value('Probing frequency')
        FreqWait = self.get_parameter_value('Settle time frequency')
        WaitDAQ = self.get_parameter_value('Acquisition delay')
        
        self.datastore.report('Starting the Schottky barrier measurement')
    
        # set the AC signal source in the LOCKIN amplifier
        
        self.LCR.setFreq(1.0e+3)
        self.LCR.setACLevelV(ACvoltage)
        self.LCR.setBias(2*ACvoltage)
        self.LCR.set_output_on()
        
        
        self.datastore.report(('Applying frequency %f' % Freq ))
        self.LCR.setFreq(Freq)
        #Sine.set_offset(ACvoltage)
        self.Stopwatch.Wait(FreqWait)
        self.LCR.auto_gain()
        for DCvoltage in DCvoltages:
            self.datastore.report(('Applying DC voltage %f' % DCvoltage ))
            self.LCR.setBias(DCvoltage)
            self.observe(DCwait, WaitDAQ)
            self.datastore.separateData()
        
        self.datastore.report('Experiment finished')
        return


from AllScripts import ScriptsBase
ScriptsBase.add_script(Test, 'Simple')
