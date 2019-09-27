# project libraries imports:
# instruments:
from GenericScript import TestScript

    
class Test(TestScript):
    def __init__(self):
        TestScript.__init__(self)
        self.Name = 'RRT protocol output chars of FET'
        self.Description = """Filed-effect transistor 'output' and 'transfer' characteristic
        Intended for fast scans utilizing the Keithley dual source meter (K 2602) unit
        with built in TSP programming \nSpecialized for the FlexNet RRT"""
        return
    def init_parameters(self):
        """
        create the list of the parameter and initialize some basic values
        """
        #voltages, acquizDelay=0.1, voltStepDelay=5
        
        
        self.generate_parameter(Name='Source-Drain (ChA) voltages', 
                                Unit='Volts',
                                Type='float', 
                                Iterable = True,
                                Limits = [ 40, -40, None], 
                                Description='List of voltages (in Volts) to be applied to the sample given order, usually between Source-Drain')
        #self.set_parameter_value('Source-Drain (ChA) voltages', [0.1,0.2])
        
        self.generate_parameter(Name='Gate-Source (ChB) voltages', 
                                Unit='Volts',
                                Type='float', 
                                Iterable = True,
                                Limits = [ 40, -40, None], 
                                Description="""List of voltages (in Volts) to be applied to the sample given order, 
                                Usually between Source and Gate.
                                This voltage is held constant, while testing a sequence of Source-Drain (ChA) voltages,
                                then the next channel 'B' voltage is applied and cycle of Source-Drain (ChA) voltages is repeated.""")
        #self.set_parameter_value('Gate-Source (ChB) voltages', [0.1,0.2])
        
        
        self.generate_parameter(Name='Source-Drain settle time',
                                Unit='Seconds', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ None, 0.001, None], 
                                Description='delay between the voltage steps in seconds')
        self.set_parameter_value('Source-Drain settle time', 0.1)
        
        self.generate_parameter(Name='Gate-Source settle time',
                                Unit='Seconds', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ None, 0.001, None], 
                                Description='delay between the voltage steps of the Channel  in seconds')
        self.set_parameter_value('Gate-Source settle time', 1.0)
        self.generate_parameter(Name='Current integration time',
                                Unit='NPLC', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ 25.0, 0.001, None], 
                                Description='Integration time of current measurement in NPLC \nNumber of Power Line Cycles, 1 PLC = 20 ms.')
        self.set_parameter_value('Current integration time', 1)
#        self.generate_parameter(Name='Device',
#                                Unit='name', 
#                                Type='name', 
#                                Iterable = False, 
#                                Limits = [ None, None, ['Keithley 617','Keithley 2602 - channel A','Keithley 2602 - channel A, fast sweep','Keithley 2602 - channel B','Keithley 2602 - channel B, fast sweep','TTi TSX3510P']], 
#                                Description='Device to measure the current voltage characteristics with')
#        self.set_parameter_value('Device', 'Keithley 617')
        return
    def init_devices(self):
        from Devices import Clock, Thermometer,SMU_FET_tester
       
        ################################################################
        ##  Here begins the initialization of devices ##################
        ################################################################
        # define and ACTIVATE the instruments
        
#        self.Channel = SMU_channelA()
#        self.append_active_devices_list(self.Channel)
#        self.Gate = SMU_channelB()
#        self.append_active_devices_list(self.Gate)
#        
        self.FET = SMU_FET_tester()
        self.append_active_devices_list(self.FET)
        
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
        
        SDvoltages = self.get_parameter_value('Source-Drain (ChA) voltages')
        self.FET.Upload_source_drain_voltages(SDvoltages)
        Gvoltages = self.get_parameter_value('Gate-Source (ChB) voltages')
        
        SDwait = self.get_parameter_value('Source-Drain settle time')
        Gwait = self.get_parameter_value('Gate-Source settle time')
        Integr = self.get_parameter_value('Current integration time')
        self.FET.cfg_measure_current_integration_time(NPLC=Integr)
        
        self.datastore.report ('Starting new FET measurement of I-V characteristic S-D for various Gate voltages')
        self.FET.set_volts(0.0,channel='a')
        self.FET.set_volts(0.0,channel='b')
        self.FET.set_output_on(channel='b') # set gate channel B output ON
        self.Stopwatch.zeroTimer()
        
        for Vgate in Gvoltages:
            self.datastore.report ('applying Gate voltage = %0.3f V' % Vgate)
            self.FET.set_volts(Vgate, channel='b')   
            self.Stopwatch.Wait(Gwait)
            self.Stopwatch.Measure()
            self.Temper.Measure()
            self.FET.MeasureSweepChannelA(SDsettle_time=SDwait)
            self.datastore.acquireData()
            self.datastore.separateData()
        
        self.FET.set_output_off(channel='b')
        self.FET.set_output_off(channel='a')
        #self.Channel.set_output_off()
        self.datastore.report('Experiment finished')
        return
                    
from AllScripts import ScriptsBase
ScriptsBase.add_script(Test, 'RRT')
