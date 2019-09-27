# the class definitions for the HAAKE F6 circulator bath
# for temperature control

from DummyMeter import Bedna
# import bus
from numpy import array
from time import sleep

class HAAKE_F6(Bedna):
    """
    the class definitions for the HAAKE F6 circulator bath
    """
    HighTlimit = -10
    LowTlimit = 120
    CoolRampLimit = 5
    HeatRampLimit = 10
    def __init__(self, BUS):
        Bedna.__init__(self, BUS)
        self.Readings = {'HAAKEtempEXT(degC)':array([]), 'HAAKEtempINT(degC)':array([]), 'HAAKEtempSET(degC)':array([])}
#        self.dev.initSequence = ['W TEC', # set temperature scale to Celsius
#                                 'IN', # set the internal control mode
#                                 #'ST'  # start the circulator temperature control and circulation
#                                 ]
#        self.init()
#       do not use usual init procedure
        self.Bus.clear()    # flush the input and output buffers
        self._set_something('W TEC')  # set temperature scale to Celsius
        #self.set_regulation_internal()  # set the internal control mode
        self.HighTlimit = self.get_high_limit()
        self.LowTlimit  = self.get_low_limit()
        return
    def _set_something(self,command=''):
        if not command == '':
            self.Bus.write_string(command)
            # obtain confirmation
            confirmation = self.Bus.read_string()
            if not confirmation == '$':
                print 'error:', confirmation
                self.Bus.clear()
                self._set_something(command)
#            print confirmation
        return
    def _get_something(self,command=''):
        if not command == '':
            self.Bus.write_string(command)
            # obtain response
            something = self.Bus.read_string()
            responseList = something.split()
#            if responseList[0] == '$':
#                print responseList
#                self._get_something(command)
        return responseList
    def set_setpoint(self, temperature):
        """
        sets the temperature setpoint in degrees C
        """
        # test if the setpoint is within limits of the instrument
        if  ( (temperature > self.LowTlimit) and (temperature < self.HighTlimit)):
            self._set_something('W SW %+.2f' % temperature)
        else:
            pass
        return
    def get_setpoint(self):
        """
        returns the temperature setpoint in degrees C
        """
        responseList = self._get_something('S')
        setpoint = float(responseList[0])
        return setpoint
    def get_temperature_internal(self):
        """
        returns the actual temperature degrees C
        from the sensor inside the bath
        """
        responseList = self._get_something('F1')
        temperature = float(responseList[0])
        return temperature
    def get_temperature_external(self):
        """
        returns the actual temperature degrees C
        from the sensor external
        """
        responseList = self._get_something('F2')
        temperature = float(responseList[0])
        return temperature
    
    def set_regulation_on(self):
        self._set_something('GO')
        return
    def set_regulation_off(self):
        self._set_something('ST')
        return
    def set_regulation_internal(self):
        self._set_something('IN')
        return
    def set_regulation_external(self):
        self._set_something('EX')
        return
    def get_high_limit(self):
        responseList = self._get_something('HL')
        limit = float(responseList[0])
        return limit
    def get_low_limit(self):
        responseList = self._get_something('LL')
        limit = float(responseList[0])
        return limit
    def Measure(self):
        #'HAAKEtempEXT(degC)':array([]), 'HAAKEtempINT(degC)':array([]), 'HAAKEtempSET(degC)':array([])}
        Text = self.get_temperature_external()
        Tint = self.get_temperature_internal()
        Setpoint = self.get_setpoint()
        
        self.Readings['HAAKEtempEXT(degC)'] = array([Text])
        self.Readings['HAAKEtempINT(degC)'] = array([Tint])
        self.Readings['HAAKEtempSET(degC)'] = array([Setpoint])
        #wats = self._get_wats()
        #self.Readings = array([wats])
        measurement_error = 0
        return measurement_error
    
        