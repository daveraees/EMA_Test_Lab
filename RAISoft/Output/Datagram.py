# Datagram.py

# major libs imports:
from numpy import array, append, hstack, zeros, resize

# project libs imports:

class MainData:
    """Define the basic data structure for the measured values and their handlers"""
    def __init__(self, deviceList=None):
        """create the arrays for the measurement"""
        self.observables = {} # yet empty list of observables
        self.deviceList = deviceList
        self.lastReadingsIndex = -1
        if not deviceList == None:
            for device in deviceList:
                self._add_observable(device)
        else:
            raise NoDeviceToMeasureError
        return
    
    def _add_observable(self, device):
        """ adds the devices headers into main datagram dictionary"""
        for unit in device.Readings.keys():
            if not self.observables.has_key(unit):
                self.observables[unit] = array([])
            else:
                print ("Ambivalent Designation of the values: %s" % unit)
        return
    
    def add_data(self):
        """ Inserts the instruments reafings into datagram """
        # find the longest array of readings
        rowMax = 1
        self.readingLast = {}
        for device in self.deviceList:
            self.readingLast.update( device.Confess() )
       
        for key in self.readingLast.keys():
            rows = len(self.readingLast[key])
            if rows > rowMax:
                rowMax = rows    # store the maximum length of reading
        
        for key in self.readingLast.keys():
            self.readingLast[key] = resize(self.readingLast[key], rowMax) # beware, if the aray is shorter than rowMax, the vacant positions will be filed with repeated array
            #print self.readingLast[key]
            self.observables[key] = hstack([ self.observables[key], self.readingLast[key] ])
        return
    def extractLastReading(self):
        """return the data from last measurement run """
        reading = self.readingLast
        return reading
    def extract_header(self):
        header = self.observables.keys()
        return header
    def extract_data(self, key=None, from_to=()):
        if not key == None:
            if from_to == ():
                data = self.observables[key]    
            else:    
                data = self.observables[key][from_to[0]:from_to[1]] # add sliced data
        return data
    def get_current_data_row(self):
        shape = self.observables[self.observables.keys()[0]].shape
        if not shape[0] == 0:
            position = shape[0] - 1
        else:
            position = 0
        return position    # the shape should be one dimensional array
        
        
    
