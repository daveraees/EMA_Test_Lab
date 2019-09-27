# this module works on measured data
# should be possible to 
#    select data region
#    perform some basic statistics
#    linear analysis

# project libraries import
#from instruments.ActiveDevicesList import devList

# major libraries import
from numpy import average,log,exp
from scipy import stats

class Analysis:
    def __init__(self, datagram):
        self.datagram = datagram # this contains the actual measured data
        markers = {}
        self.markers = markers.fromkeys( self.datagram.extract_header(),(0,0))    # tuple contains data line markers in (from,to) range form
        return
    def mark_from(self, keys=()):
        """construct (begin,end) form of a tuple """
        if keys == ():
            keys = self.markers.keys()
        for key in keys:
            self.markers[key] = (self.datagram.get_current_data_row()+1, self.markers[key][1])
    def mark_to(self, keys=()):
        if keys == ():
            keys = self.markers.keys()
        for key in keys:
            self.markers[key] = (self.markers[key][0], self.datagram.get_current_data_row())
    def get_markers(self):
        return self.markers
    def average_marked(self, key):
        """calculate average value of previously marked range of readings from key"""
        value = average(self.datagram.extract_data( key, from_to=self.markers[key]))
        return value
    def average_last(self, key, number):
        """calculate average value of last 'number' of readings from key"""
        position = self.datagram.get_current_data_row()
        value = average(self.datagram.extract_data( key, from_to=(position-number,position)))
        return value
    def linear_regres_marked(self, key_independent, key_dependent):
        independent = self.datagram.extract_data( \
                                key_independent, \
                                from_to=self.markers[key_independent])
        dependent = self.datagram.extract_data( \
                                key_dependent, \
                                from_to=self.markers[key_dependent])
        #print independent, dependent
        (slope,intercept,r,tt,stderr)= stats.linregress(independent, dependent)
        #print 'slope', slope, 'intercept', intercept
        first_coordinate = (independent[0], intercept + independent[0]* slope)
        return (intercept, slope, first_coordinate, r, tt, stderr)
    def AE_marked(self, key_temerature, key_current):
        independent = self.datagram.extract_data( \
                                key_temerature, \
                                from_to=self.markers[key_temerature]).copy()
        dependent = self.datagram.extract_data( \
                                key_current, \
                                from_to=self.markers[key_current]).copy()
        independent = 1.0 / (273.15 + independent)    # convert the data into reciprocal temperatures
        dependent = log(dependent)    # NATURAL logarithm
        (slope,intercept,r,tt,stderr)= stats.linregress(independent, dependent) # simple linear regression
        energy = -slope * 8.62e-5 # recalculation to electronvolts 
        zeroKcurrent = exp(intercept)
        return (energy,zeroKcurrent,r,tt,stderr)