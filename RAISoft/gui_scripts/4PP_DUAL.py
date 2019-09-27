# project libraries imports:
# instruments:
from GenericScript import TestScript

    
class Test(TestScript):
    def __init__(self):
        TestScript.__init__(self)
        self.Name = '4-Point-Probe Resistance'
        self.Description = """
    This can be used for measurement with the linear array four-point-probe
    Channel A is used to measure voltage in the inner pait of the contacts
    Channel B  Sources the current into the outer pair contacts
    """
        return
    def init_parameters(self):
        """
        create the list of the parameter and initialize some basic values
        """
        #voltages, acquizDelay=0.1, voltStepDelay=5
                
        
        self.generate_parameter(Name='Tested currents', 
                                Unit='Amperes',
                                Type='float', 
                                Iterable = True,
                                Limits = [ 0.001, 0.0, None], 
                                Description='List of current values (in Amperes) to be applied to the sample outer contacts')
        #self.set_parameter_value('Tested currents', [0.1,0.2])
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
        return
    def init_devices(self):
        from Devices import Clock,SMU_4PP_tester
        self.Elmeter = SMU_4PP_tester()
        self.append_active_devices_list(self.Elmeter)
        self.Stopwatch = Clock()
        self.append_active_devices_list(self.Stopwatch)
    def _run(self):
        """ simple current-voltage characteristics measurement """
        ################################################################
        ##  Here begins the experimetal part ###########################
        ################################################################
        
        # switch on the voltage source:
        currents = self.get_parameter_value('Tested currents')
        amperStepDelay = self.get_parameter_value('Acquisition time')
        acquizDelay = self.get_parameter_value('Acquisition delay')
        
        self.Elmeter.set_amperes(0.0, channel='a')
        self.Elmeter.set_amperes(0.0, channel='b')
        self.Elmeter.set_output_on(channel='a')
        self.Elmeter.set_output_on(channel='b')
        for amps in currents:
            self.Elmeter.set_amperes(amps)
            self.observe(amperStepDelay, acquizDelay)
            self.datastore.separateData()
        #self.Elmeter.set_amperes(0.0, channel='a')
        self.Elmeter.set_amperes(0.0, channel='b')
        self.Elmeter.set_output_off(channel='a')
        self.Elmeter.set_output_off(channel='b')
        return
            


from AllScripts import ScriptsBase
ScriptsBase.add_script(Test, 'Simple')
