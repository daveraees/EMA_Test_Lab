# project libraries imports:
# instruments:
from GenericScript import TestScript



class Test(TestScript):
    def __init__(self):
        TestScript.__init__(self)
        self.Name = 'Simulated sawtooth generator'
        self.Description = """ Script for testing the device independent part of the program"""
        return
    def init_parameters(self):
        """
        create the list of the parameter and initialize some basic values
        """
        #voltages, acquizDelay=0.1, voltStepDelay=5
        #slopeList, acquizDelay=0.1, acquizTime=6
        self.generate_parameter(Name='List of slopes', 
                                Unit='arb. u.',
                                Type='float',
                                Iterable = True,  
                                Limits = [ 100, -100, None], 
                                Description='List of slopes to be generated to the sample given order')
        #result = self.set_parameter_value('List of slopes', [0.1,0.2])
        #print 'slopeList set', result
        self.generate_parameter(Name='Acquisition delay',
                                Unit='Seconds', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ None, None, [0.01, 0.1, 1.0, 1e1, 1e2]], 
                                Description='delay of the data acquizition loop in seconds')
        self.set_parameter_value('Acquisition delay', 0.1)
        self.generate_parameter(Name='Acquisition time',
                                Unit='Seconds', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ None, 0.001, None], 
                                Description='delay between the voltage steps in seconds')
        self.set_parameter_value('Acquisition time', 5.0)
        self.generate_parameter(Name='Repetitions count',
                                Unit='count', 
                                Type='count', 
                                Iterable = False, 
                                Limits = [ 999, 1, None], 
                                Description='how many times to repeat the entire test')
        self.set_parameter_value('Repetitions count', 1)
        return
    def init_devices(self):
        from DummyDevices import Clock,GeneratorLine
        ################################################################
        ##  Here begins the initialization of devices ##################
        ################################################################
            
        # define and ACTIVATE the instruments
        self.Stopwatch = Clock()
        self.append_active_devices_list(self.Stopwatch)
        self.Line = GeneratorLine()
        self.append_active_devices_list(self.Line)
        return
    def _run(self):
        
        slopeList = self.get_parameter_value('List of slopes')
        acquizTime = self.get_parameter_value('Acquisition time')
        acquizDelay = self.get_parameter_value('Acquisition delay')
        repeatTimes = self.get_parameter_value('Repetitions count')
        #print slopeList,acquizTime,acquizDelay
        for roundNumber in range(repeatTimes):
            for slope in slopeList:
                offset = slope / 10.0
                self.Line.setOffset(offset)
                self.Line.setSlope(slope)
                self.datastore.analysis.mark_from()
                #begin DATA ACQUISITION script here:
                self.datastore.report(('starting data generation. Slope>', slope, 'offset:', offset))  
                self.observe(acquizTime, acquizDelay)
                self.datastore.separateData()
                self.datastore.report(('data gen finished, starting analysis'))
                self.datastore.analysis.mark_to()
                self.datastore.report(( 'analysing data in range', self.datastore.analysis.get_markers()))
                self.datastore.report(('average:', self.datastore.analysis.average_marked("U(V)")))
                self.datastore.report(( 'average last 10 points:', self.datastore.analysis.average_last('U(V)',10)))
                self.datastore.report(( 'linear regression:', self.datastore.analysis.linear_regres_marked("time(s)", "U(V)")))

    
from AllScripts import ScriptsBase
ScriptsBase.add_script(Test, 'Dry run')
