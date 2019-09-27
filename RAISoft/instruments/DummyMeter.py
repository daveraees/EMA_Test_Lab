# this code should create a virtual measurement device used for progrem development

# library imports
import random
from numpy import array, sin

# project libraries import
from ActiveDevicesList import devList
from LocalTimer import LocalTimerClass

class deviceState:
    initialized = False
    ready_to_measure = False
    awaiting_response = False
    setpoint_ready = False
    trouble = False
class devInfo:
    Name = "NoName"
    Adrs = "NoAdrs"
    initSequence = []

class Bedna:
    #Bus = None
    #Units = () # Indicate the reading physical unit
    Readings = {} # dictionary: {"desighation":array(reading)}
    BadReadings = ()    # Some readings may be bad. give their indexes in the tuple
    datagramFirstIndex = None
    Timestamps = array([]) # give array of timestamps of the each reading 
    def __init__(self,BUS, Identificator=None):
        self.Bus = BUS
        self.dev = devInfo()
        self.status = deviceState()
        self.Timer = LocalTimerClass()
        self.isActive = False
        if Identificator == '':
            self.dev.Name = self.Bus.ident()
        else:
            self.dev.Name = Identificator
        return
    def Activate(self):
        """ Adds itself to the list of activated devices """
        devList.append(self)    # for command line scipts
        self.setActive(True)
        
        return
    def Close(self):
        if self.Bus != None:
            self.Bus.close()
        return
    
    def Measure(self):
        """Templeate function for Data Acquisition purposes"""
        raise NotImplementedError
    
    def Set(self, value):
        """Function for purpose, when the device is used as Valve in Regulator"""
        raise NotImplementedError
    def Read(self):
        """Function for purpose, when the device is used as Sensor in Regulator
        it should return the single float (e.g. temperature in deg.C)
        it is not for data acquisition purposes. For this use Measure()"""
        raise NotImplementedError
    def Confess(self, quantity=None):
        """Return the readings obtained during last measurement run"""
        if quantity == None:
            readings = self.Readings
        else:
            if self.Readings.has_key(quantity):
                readings = self.Readings[quantity]
            else:
                readings = None
        return readings
    def init(self):
        for command in self.dev.initSequence:
            self.Bus.write_string(command)
            self.Timer.Wait(0.2)
        return
    def setActive(self,active=True):
        """ sets itself active for purpose of data collection activated devices """
        if active:
            self.isActive = True
        else:
            self.isActive = False
        return
    def getActive(self):
        """ returns active flag for purpose of data collection activated devices """
        return self.isActive
    


class GeneratorLine(Bedna):
    def __init__(self):
        Bedna.__init__(self, BUS=None)
        self.dev.Name = "Generator harmonickeho signalu"
        #self.Units = ("U (V)",)    # a tuple of measurement value`s units
        self.Readings = {"U(V)":array([])}
        self.Timer = LocalTimerClass()
        self.Timer.zeroTimer()
        self.slope=10.0
        self.offset=-0.2
        return
    def setSlope(self,slope):
        self.slope = slope
        return
    def getSlope(self):
        return self.slope
    def setOffset(self,offset):
        self.Timer.zeroTimer()
        self.offset = offset
        return
    def getOffset(self):
        return self.offset
    def Measure(self):
        timestamp = self.Timer.getTotalTime()
        #self.Timestamps = array([timestamp])
        self.Readings["U(V)"] = array([self.slope * self.Timer.getSinceLastZeroed() + self.offset])
        measurement_error = 0
        return measurement_error

class GeneratorSin(Bedna):
    def __init__(self):
        Bedna.__init__(self, BUS=None)
        self.dev.Name = "Generator pulzu signalu"
        #self.Units = ("U (V)",)    # a tuple of measurement value`s units
        self.Readings = {"Ur(V)": array([]), "Ir(A)":array([])}
        self.Timer = LocalTimerClass()
        return

    def Measure(self):
        voltages = range(100)
        self.Readings["Ur(V)"] = array(voltages)
        #self.Timestamps = array([timestamp])
        self.Readings["Ir(A)"] = array( sin(voltages))
        measurement_error = 0
        return measurement_error
