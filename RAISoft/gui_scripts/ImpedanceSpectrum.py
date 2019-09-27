# project libraries imports:
# instruments:
from GenericScript import TestScript

class Test(TestScript):
    def __init__(self):
        TestScript.__init__(self)
        self.Name = 'Impedance frequency spectrum'
        self.Description = """Measurement of the Impedance frequency spectrum"""
        return
    def init_parameters(self):
        """
        create the list of the parameter and initialize some basic values
        """
        
        self.generate_parameter(Name='Tested frequencies', 
                                Unit='Hz',
                                Type='float', 
                                Iterable = True,
                                Limits = [ 1e5, 0.01, None], 
                                Description='List of modulation frequencies')
        #self.set_parameter_value('Tested frequencies', 64)
        
        self.generate_parameter(Name='AC voltage',
                                Unit='Volts', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ 4.5, 0.0, None], 
                                Description='Signal of AC voltage to be applied')
        self.set_parameter_value('AC voltage', 0.05)
        
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
        
        self.generate_parameter(Name='Chopper device',
                                Unit='', 
                                Type='name', 
                                Iterable = False, 
                                Limits = [ None, None, ['SRS Lock-In Amp','HIOKI LCR HI-TESTER']], 
                                Description="""Device to provide measurement.""")
        self.set_parameter_value('Chopper device', 'SRS Lock-In Amp')
        return
    def init_devices(self):
        from Devices import Clock, Thermometer,\
                            LCR_LockIn, LCR_HIOKI
                            
        
        
        
        deviceName = self.get_parameter_value('Chopper device')
        if deviceName == 'SRS Lock-In Amp':
            self.Channel = LCR_LockIn()
            self.append_active_devices_list(self.Channel)
        if deviceName == 'HIOKI LCR HI-TESTER':
            self.Channel = LCR_HIOKI()
            self.append_active_devices_list(self.Channel)
        #from instruments.Keithley import Electrometer617
        #from instruments.Agilent import A34401_4ohm
        ################################################################
        ##  Here begins the initialization of devices ##################
        ################################################################
        # define and ACTIVATE the instruments
        
        #PeltierP = PID_CBdriver(TCchannel=1, count=20)
        #PeltierP.Activate()

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
        
        Frequencies = self.get_parameter_value('Tested frequencies')
        ACvoltage = self.get_parameter_value('AC voltage')
        WaitWL = self.get_parameter_value('Settle time frequency')
        WaitDAQ = self.get_parameter_value('Acquisition delay')
        
        self.datastore.report('Using device "%(device)s" for measurement'  % \
            {'device':deviceName})
        
        # initializing the measurement for given instrument:
        if deviceName == 'SRS Lock-In Amp':
            self.Channel.setACLevelV(ACvoltage)
            self.Channel.setFreq(Frequencies[0])
            self.Channel.auto_gain()
            self.Stopwatch.Wait(3)
            
        # initializing the measurement for given instrument:
        if deviceName == 'HIOKI LCR HI-TESTER':
            self.Channel.setACLevelV(ACvoltage)
            self.Channel.setFreq(Frequencies[0])
            self.Stopwatch.Wait(3)
        
                
        #self.datastore.report ('estimation of LockIn amplifier gain for desired Frequencies:')
    
        self.datastore.report('Starting the impedance spectra measurement from %(from)f to %(to)f Hz'  % \
            {'from':Frequencies[0], 'to':Frequencies[-1]})
        self.datastore.report ('Starting Frequency scanning:')
        for freq in Frequencies:
            self.Channel.setFreq(freq)
            self.datastore.report ('Set New frequency: %0.2f' % freq)
            if deviceName == 'SRS Lock-In Amp':
                if freq > 0.01:
                    gain = self.Channel.auto_gain()
                    #self.datastore.report('Found new Lock-In Amplifier GAIN: %d' % gain)
                else:
                    gain = self.Channel.LockIn.get_gain()
                    #self.datastore.report('Kept old Lock-In Amplifier GAIN: %d' % gain)
            minimumWait = WaitWL + 10/freq
            self.observe(minimumWait, WaitDAQ)
            self.datastore.separateData()
            
        self.datastore.report ('Experiment finished')
        
        if deviceName == 'SRS Lock-In Amp':
            #self.Lamp.set_output_off()
            #self.Filter.close_shutter()
            #self.Channel.set_aux_output(channel=2, voltage=1.0)
            pass
        if deviceName == 'HIOKI LCR HI-TESTER':
            #self.Chopper.set_output_off()
            pass
        self.Channel.Close()
        #self.datastore.report('finished the Modulated frequency photocurrent spectrum measurement')
        return

from AllScripts import ScriptsBase
ScriptsBase.add_script(Test, 'Photoconductivity')