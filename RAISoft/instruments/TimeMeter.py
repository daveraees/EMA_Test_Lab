# Module for timing purposes

# numy
from numpy import array
from time import time, clock, sleep

# my imports
from DummyMeter import Bedna


from LocalTimer import LocalTimerClass

class MainTimerClass(Bedna):
    timer = LocalTimerClass()
    def __init__(self):
        """record the starting time of object creation"""
        Bedna.__init__(self,None)        
        self.dev.Name = "Timer"
        self.Readings = { "time(s)": array([]) }
        # timer specific
        self.pocatek = time()
        self.sinceLastZeroed = time()
        return
    
    def Wait (self, casCekani):
        sleep (casCekani)
        return
    def getTotalTime(self):
        return time() - self.pocatek
    def Measure(self):
        timestamp = self.getTotalTime()
        self.Timestamps = array([timestamp])
        self.Readings["time(s)"] = array([timestamp])
        measurement_error = 0
        return measurement_error
    def getSinceLastZeroed(self):
        return time() - self.sinceLastZeroed
    def zeroTimer(self):
        aktual = self.getTotalTime()
        self.sinceLastZeroed = time()
        return aktual
    def Close(self):
        return
