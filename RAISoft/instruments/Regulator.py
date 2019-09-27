# This should define the abstract regulator
import threading
from LocalTimer import LocalTimerClass
from DummyMeter import Bedna
from numpy import array

class Regulator(Bedna):
    class Feedback:
        prop = 0.1
        loopTime = 1
        measLoopTime = loopTime
        memory = None
        signal = None
    class setpointInfo:
        reached = threading.Event()
        ready = False
        valid = False
        timestamp = 0.0
        evaluatePeriod = 0.0
        sigma = 0.0
        loopCounter = 1
        deviation = 0.0
        value = 0.0    # value of the setpoint
        actualValue = 0.0    # reading of the sensor
        pastValue = 0.0    # previous reading of the sensor
        tolerance = 0.0
    fb = Feedback()
    setpoint = setpointInfo()
    state = True    # Do regulation looping?
    def __init__(self, Valve=None, Sensor=None, looptime=None,):
        self.valve = Valve
        self.sensor = Sensor 
        #self.valve.init()
        #self.sensor.init()
        self.timer = LocalTimerClass()
        self.regulation = threading.Thread(target=self._regLoop, name='RegulatorLoop') 
        self.setpoint.reached.clear()
        if not (looptime == None): 
            self.fb.loopTime = looptime
    
        # initialize the output
        self.Readings = {'SPage(s)':array([]), 'sigma()':array([])}    # t is time since the setpoint was reached, sigma is mean square deviation
        return
    def setNew_setpoint(self, value, tolerance, evalPeriod):
        self.cancelRamping()    # if there is ramp going on stop it
        self.setpoint.reached.clear()
        self.setpoint.value = float(value)
        self.setpoint.tolerance = float(tolerance)
        self.setpoint.evaluatePeriod = float(evalPeriod)
        self.setpoint.timestamp = self.timer.getTotalTime()
        self.setpoint.valid = True
        print ('New setpoint activated: %f' % value)
        return
    def getSetpoint(self):
        return self.setpoint.value
    def waitForSetpoint(self, timeout=None):
        self.setpoint.reached.wait(timeout)
        return 
    def Measure(self):
        raise NotImplementedError
    def _evaluate(self):
        "See, if the setpoint value has been reached and wait an evaluation period before claiming the setpoint reached"
        self._measure_sensor()
        time = self.timer.makeTimestamp()
        self.setpoint.deviation = self.setpoint.actualValue - self.setpoint.value
        if (abs(self.setpoint.deviation) < abs(self.setpoint.tolerance)):
            if not self.setpoint.valid:
                self.setpoint.valid = True
                self.setpoint.timestamp = self.timer.makeTimestamp()
            else:
                if not self.setpoint.ready:
                    if self.setpoint.evaluatePeriod < (time - self.setpoint.timestamp):
                        self.setpoint.ready = True
                        print ('New setpoint evaluated: %f' % self.setpoint.value)
                        self.setpoint.reached.set()    # set the event setpoint reached !!!
                        self.setpoint.sigma = 0.0    # zero the statistics
                        self.setpoint.loopCounter = 1    # zero the counter
                else:
                    self.setpoint.loopCount = self.setpoint.loopCounter + 1 
        else:
            self.setpoint.valid = False
            self.setpoint.ready = False
            self.setpoint.sigma = 0.0    # zero the statistics
            self.setpoint.loopCounter = 1    # zero the counter
        return
    def _calculateNew(self):
        #self.fb.memory = self.fb.signal
        #signal = self.fb.prop * (self.setpoint.actualValue - self.setpoint.value)
        #self.fb.signal = signal
        pass
        raise NotImplemetedError 
    def _adjust(self):
        #print self.setpoint.value,self.setpoint.actualValue, self.fb.signal
        self.valve.Set(self.fb.signal)
        return
    def _regLoop(self):
        while True:
            if self.state:
                self.fb.measLoopTime = self.timer.zeroTimer()
                self._evaluate()
                self._collect_statistics()
                self._calculateNew()
                self._adjust()
                self.timer.Wait(self.fb.loopTime)
            else:
                pass
        return
    def _collect_statistics(self):
        if self.setpoint.ready:
            dev = self.setpoint.deviation
            sqDev = dev * dev
            self.setpoint.sigma = self.setpoint.sigma + sqDev
        return
    def linRamp(self, difference=0.0, duration=0.0):
        """ spans a ramping thread in background which manipulates the setpoint by given parameters """
        class ramp(threading.Thread):
            def __init__(self, difference,duration,regulator):
                threading.Thread.__init__(self)
                self.diff = difference    # ramp height in regulator units
                self.duration = duration      # ramp duration in seconds
                self.regulator = regulator
                self.clock = LocalTimerClass()
                self.clock.zeroTimer()
                self.roughness = 1 # how many (approx) regulator steps should be taken before changing the setpoint?
                self.whiteflag = False
                return
            def run(self):
                elapsed = 0.0
                originalValue = self.regulator.setpoint.value
                while elapsed < self.duration:
                    self.clock.Wait( self.roughness * self.regulator.fb.loopTime)
                    elapsed = self.clock.getSinceLastZeroed()
                    # manipulate the regulator setpoint:
                    if self.whiteflag: 
                        break # terminate the ramping loop
                    else:
                        value = originalValue + (self.diff / self.duration * elapsed)
                        self.regulator.setpoint.value = value
                return
            def stop(self):
                """ terminates the ramping Loop """
                self.whiteflag = True
                return
        self.ramp = ramp(difference, duration, self)
        self.ramp.start()
        return
    def rampingInProgress(self):
        try:
            alive = self.ramp.isAlive()
        except:
            alive = False
        return alive
    def cancelRamping(self):
        if self.rampingInProgress():
            self.ramp.stop()
    def startRegulation(self):
        self.regulation.setDaemon(True)
        self.regulation.start()
        return
    def regulate(self, state):
        "set the regulation active or inactive"
        self.state = bool(state)
        return
    def _measure_sensor(self):
        raise NotImplementedError
    

