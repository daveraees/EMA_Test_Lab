from numpy import array
import threading
#from time import sleep
from DummyMeter import Bedna

class Cornerstone130 (Bedna):
    def __init__(self, BUS):
        """
        Control of the monochromator ORIEL
        """

        Identificator = "Oriel Instruments,Model 74000 Cornerstone 130,SN0,V01.60"
        Bedna.__init__(self, BUS)
        self.Readings = {'Wavelength(nm)': array([]),}    # define the units of the measurement readings
        self.Bus.clear()
        self.dev.initSequence = [('HANDSHAKE 0'),   # set the instrument to report status byte after comleting in instruction
                                 ('UNITS NM' ), # set the  wl. units to Nanometres
                                 ]
        # some useful constants                         ] 
        self.limitMAXWL = 1600 # limit of the source in amperes
        self.limitMINWL = 180  # limit of the voltage source in volts
        # actual parameters of the device encored in numerical values
        self.init()
        self.wavelength = 300.0 # current wl.
        #self.get_wave() 
        self.shutter_open = self.get_shutter()
        #self.get_shutter()
        return
    def set_wave(self, wavelength):
        """ Sets the desired wavelength (in nanometers)"""
        if wavelength > self.limitMAXWL:
            wavelength = self.limitMAXWL
        if wavelength < self.limitMINWL:
            wavelength = self.limitMINWL
        # enter verification mode to get the message when operation completed
        self.Bus.write_string('HANDSHAKE 1')
        confirmation = self.Bus.read_string(0.1)
        self.Bus.write_string('GOWAVE %3.3f' % wavelength)
        confirmation = self.Bus.read_string(20)     # going to some wl can take some time
        if not (confirmation == '0'):
            print 'Monochromator Error'
            self.Bus.clear()
            print self.Bus.read_string(timeout=0.1)
        self.Bus.write_string('HANDSHAKE 0')
        self.wavelength = self.get_wave()
        #self.wavelength = wavelength
        return
    def get_wave(self):
        """ do NOT use this"""
        response = self.Bus.Query('WAVE?',timeout=0.2)
        #print response
        self.wavelength = float(response)
        return self.wavelength
    #def zero_order(self):
    #    self.Bus.write_string('GOWAVE 000.000\n')
    #    self.wavelength = self.get_wave()
    def get_shutter(self):
        """ do NOT use this"""
        shutter = self.Bus.Query('SHUTTER?')
        if shutter == 'O':
            self.shutter_open = True
        else:
            self.shutter_open = False
        return self.shutter_open
    def open_shutter (self):
        self.Bus.write_string('SHUTTER O')
        #self.shutter_open = self.get_shutter()
        self.shutter_open = True
        return
    def close_shutter (self):
        self.Bus.write_string('SHUTTER C')
        #self.shutter_open = self.get_shutter()
        self.shutter_open = False
        return
    def _shutterTimer(self):
        """
        shutter timing
        """
        self.set_wave(self.shutterTimer.Wavelength)
        self.close_shutter()
        self.Timer.zeroTimer()
        while self.shutterTimer.TimeOFF > self.Timer.getSinceLastZeroed():
            pass
        for cycle in range(self.shutterTimer.cyclesN):
            self.open_shutter()
            self.Timer.zeroTimer()
            while self.shutterTimer.TimeON > self.Timer.getSinceLastZeroed():
                pass
            self.close_shutter()
            self.Timer.zeroTimer()
            while self.shutterTimer.TimeOFF > self.Timer.getSinceLastZeroed():
                pass
            self.Timer.zeroTimer()
        #self.shutterTimer=None   
        return    
    def blick(self,Wavelength,TimeON,TimeOFF,cyclesN=1):
        """
        strats a thread controling the timing of the shutter
        """
        self.shutterTimer = threading.Thread(target=self._shutterTimer, name='shutterTimer') 
        self.shutterTimer.setDaemon(False)
        self.shutterTimer.Wavelength = Wavelength
        self.shutterTimer.TimeON = TimeON
        self.shutterTimer.TimeOFF = TimeOFF
        self.shutterTimer.cyclesN = cyclesN
        self.shutterTimer.start()
        return    
            
    def Measure(self):
        """
        only reads the program driver buffer !!!
        """
        self.Readings['Wavelength(nm)'] = array([self.wavelength])
        measurement_error = 0
        return measurement_error
