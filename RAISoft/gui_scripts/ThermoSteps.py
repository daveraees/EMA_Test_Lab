# project libraries imports:
# instruments:
from GenericScript import TestScript
import numpy

class Test(TestScript):
    def __init__(self):
        TestScript.__init__(self)
        self.Name = 'Temperature control'
        self.Description = """Sets the thermostat temperature 
        and waits for stabilization"""
        return
    def init_parameters(self):
        """
        create the list of the parameter and initialize some basic values
        """
        
        self.generate_parameter(Name='NEW temperature',
                                Unit='Celsius', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ 120, -40.0, None], 
                                Description='Temperature to be reached by HAAKE thermostat inside the sample chamber')
        self.set_parameter_value('NEW temperature', 0.05)
        
        self.generate_parameter(Name='Acquisition delay',
                                Unit='Seconds', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ None, None, [1, 2, 5, 10, 20, 40]], 
                                Description='delay of the subsequent temperature readings in seconds')
        self.set_parameter_value('Acquisition delay', 2)
        
        self.generate_parameter(Name='Stabilization period',
                                Unit='Minutes', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ None, 1.0, None], 
                                Description='How long the reached stable temperature should be kept')
        self.set_parameter_value('Stabilization period', 5.0)
        
        self.generate_parameter(Name='Stabilization tolerance',
                                Unit='Celsius', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ None, 0.01, None], 
                                Description='How how much the temperature can vary in the "stabilized" condition')
        self.set_parameter_value('Stabilization tolerance', 0.05)
        
        return
    def init_devices(self):
        from Devices import Clock, Thermostat
                            
        
        
        
        self.Thermostat = Thermostat()
        self.append_active_devices_list(self.Thermostat)
        self.Stopwatch = Clock()
        self.append_active_devices_list(self.Stopwatch)
        
    def _run(self):
        """ simple current-voltage characteristics measurement """
        ################################################################
        ##  Here begins the experimetal part ###########################
        ################################################################
        
        Setpoint =  self.get_parameter_value('NEW temperature')
        WaitDAQ = self.get_parameter_value('Acquisition delay')
        WaitSetpoint = self.get_parameter_value('Stabilization period')
        Tolerance = self.get_parameter_value('Stabilization tolerance')
        WaitSetpointSeconds = WaitSetpoint * 60.0
        
        self.datastore.report('Setting the thermostat HAAKE to NEW temperature setpoint: %(Setpoint)+0.2f degrees Celsius'  % \
            {'Setpoint':Setpoint})
        
        self.Thermostat.set_regulation_external()
        self.Thermostat.set_regulation_on()
        
        self.Thermostat.set_setpoint(Setpoint)
        self.Thermostat.Measure()
        self.Stopwatch.Measure()
        self.datastore.acquireData()
        # get the timer key:
        keyTimer = self.Stopwatch.Readings.keys()[0]
        keyTemperature = 'HAAKEtempEXT(degC)'
        # main data acquisistion loop
        while True:
            # periodically check the actual tempearure and evaluate the deviation
            self.Stopwatch.Wait(WaitDAQ)
            self.Thermostat.Measure()
            self.Stopwatch.Measure()
            self.datastore.acquireData()
            # get the timestaps of the temperature readings: 
            timestamps = self.datastore.datagram.extract_data(key=keyTimer)
            historicalTimestamp = timestamps[-1] -   WaitSetpointSeconds
            # if the measurement history is long enough, find an index 
            if historicalTimestamp > 0:
                # if the measurement history is long enough, find an index of recent reading
                historicalIndex = numpy.searchsorted(timestamps,historicalTimestamp)
                historicalTemperatures = self.datastore.datagram.extract_data(key=keyTemperature,from_to=([historicalIndex,None]))
                #filter for reading errors
                historicalTemperatures = numpy.delete(historicalTemperatures, numpy.argwhere(historicalTemperatures==-1e999))
                # calcualte the root mean square of the deviation of the recent temperature readings :
                TempSTD = numpy.std(historicalTemperatures)
                #self.datastore.report('%d, %f, %f' % historicalIndex, historicalTimestamp, TempSTD)
                print 'standard deviation of measured temperature:', TempSTD
                if len(historicalTemperatures) > 2:
                    if TempSTD < Tolerance:
                        break
        
        return
                
from AllScripts import ScriptsBase
ScriptsBase.add_script(Test, 'Thermostated')
 
       