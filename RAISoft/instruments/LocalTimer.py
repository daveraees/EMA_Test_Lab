# This C defines the timer for usage in each device for the regulation loop purposes
#main python library import
from time import time, clock, sleep


class LocalTimerClass:
    def __init__(self):
        """record the starting time of object creation"""
        # timer specific
        self.pocatek = time()
        self.sinceLastZeroed = time()
        return
    def Wait (self, casCekani):
        sleep (casCekani)
    def getTotalTime(self):
        return time() - self.pocatek
    def getSinceLastZeroed(self):
        return time() - self.sinceLastZeroed
    def zeroTimer(self):
        aktual = self.getSinceLastZeroed()
        self.sinceLastZeroed = time()
        return aktual
    def makeTimestamp(self):
        return time()
    def Close(self):
        return