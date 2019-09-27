

# major libraries import
from numpy import array, concatenate

#project libraries import
from Regulator import Regulator
#from TTi import PStsx3510P
#from Agilent import A34401_temp

class PIDHeater(Regulator):
    """
    Provides P-I-D temperature regulation using 10 A power source
    and temperature platinum resistor temperature sensor
    """
    class PIDregul:
        Kp = 0.1   # gain
        Ti = 0.0    # Integral Time
        Tii = 0.0    # Integral time
        Td = 0.0    # Derivative time
        P = 0.0
        I = 0.0
        D = 0.0
        error = None
        pastError = None
    def __init__(self, Valve, Sensor, Kp=0.1, Ti=None, Td=None, looptime=None):
        if looptime == None:
            loopTime = 1.0    # default regulator loop time 1s
        Regulator.__init__(self, Valve, Sensor, looptime)
        #self.sensor = sensor
        #self.valve = valve
        self.valve.Set(0)
        self.valve.set_output_on()
        self.Readings.update(self.sensor.Readings) # include the readings of the sensor
        self.Readings.update(self.valve.Readings)    # Valve readings are unnecessary
        self.valveError = 0
        self.senseError = 0
        self.pid = self.PIDregul()
        self.set_PID_params(Kp, Ti, Td, looptime)
        return
    def Measure(self):
        if self.setpoint.ready:
            timestamp = self.timer.makeTimestamp()
            setpointOldness = timestamp - self.setpoint.timestamp
            sigma = self.setpoint.sigma / self.setpoint.loopCounter
            self.Readings['SPage(s)'] = array([setpointOldness])
            self.Readings['sigma()'] = array([sigma])
            setpointError = 0
        else:
            self.Readings['SPage(s)'] = array([0.0])
            self.Readings['sigma()'] = array([0.0])
            setpointError = 1    # 1 = setpoint invalidated
            
        self.Readings.update(self.sensor.Readings) # include the readings of the sensor
        self.Readings.update(self.valve.Readings)    # and valve
        measurement_error = self.senseError + 100 * self.valveError + 1000 * setpointError
        return measurement_error
    def _calculateNew(self):  # implemented PID regulator
        if not self.pid.error == None:
            self.pid.pastError = self.pid.error
        else:
            self.pid.pastError = 0
        self.pid.error = - self.setpoint.deviation
        if self.valve.out_of_bounds:        # eliminate integrator windup
            self.pid.Ti = None
        else:
            self.pid.Ti = self.pid.Tii
        if not self.pid.Ti == None:
             self.pid.I = self.pid.I +  self.fb.measLoopTime / self.pid.Ti * self.pid.error 
        else:
            self.pid.I = 0
        if not self.pid.Td == None:
            self.pid.D = (self.pid.error - self.pid.pastError) / self.pid.Td / self.fb.measLoopTime
        else:
            self.pid.D = 0
        signal = self.pid.Kp * (self.pid.error + self.pid.I + self.pid.D)    
        self.fb.signal = signal
        return 
    def _adjust(self):
        #print 'setpoint:', self.setpoint.value, self.fb.signal, self.setpoint.valid, self.setpoint.ready
        #print 'error:', self.pid.error , 'I:', self.pid.I , 'D:', self.pid.D, 'Kp:' , self.pid.Kp  
        self.valve.Set(self.fb.signal)
        return 
    def _measure_sensor(self):
        self.senseError = self.sensor.Measure()      # get the instrumnet reading 
        self.valveError = self.valve.Measure()
        keys = self.sensor.Readings.keys()
        value = self.sensor.Readings[keys[0]]    # first field in array is reading from the sensor
        self.setpoint.actualValue = value
        return value
    def set_PID_params(self, Kp, Ti=None, Td=None, looptime=None):
        self.pid.Kp = Kp
        self.pid.Ti = Ti
        self.pid.Tii = Ti
        self.pid.Td = Td
        if not (looptime == None): 
            self.fb.loopTime = looptime
        else:
            self.fb.loopTime = 1.0
        self.resetI()
        return 
    def resetI(self):
        self.pid.I = 0.0
        return
