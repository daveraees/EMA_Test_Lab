#from GPIBdevices import GPIBDevice
#from SERIALdevices import SERIALDevice
from DummyMeter import Bedna
# import bus
from numpy import array
from time import sleep

class PStsx3510P(Bedna):
    """    
        # test PowerSource
        from threading import Thread
        from time import sleep
        import random
        
        PowerSource = PStsx3510P('PowerSourceTTi')
        
        
        def Source():  
            while True:
                PowerSource.set_volts(random.random())
                PowerSource.Measure()
                #PowerSource.OUTqueue.join()
                print 'source:',  PowerSource.Readings
                sleep(0.5)
            return
        
        def Valve():
            while True:
                #PT100.Measure()
                sleep(0.5)
                PowerSource.Set(random.random())
                PowerSource.Measure()
                #PowerSource.OUTqueue.join()
                print 'valve:', PowerSource.Readings
            return
        
        source = Thread(target=Source)
        valve = Thread(target=Valve)
        
        source.setDaemon(True)
        valve.setDaemon(True)
        source.start()
        valve.start()
        
        valve.join(50)
        source.join(54)

    """
    sleeptime = 0.1
    def __init__(self, BUS):
        Bedna.__init__(self, BUS)
        self.Readings = {'U(V)':array([]), 'I(A)':array([])}
        self.dev.initSequence = ['I 1.0']
        self.init()
        self.limitA = self.get_amperes_limit()
        self.out_of_bounds = 0
        return
    def _assert_OPC(self):
        self.Bus.write_string('*OPC')
        return
    def Measure(self):
        volts = self._get_volts()
        amperes = self._get_amperes()
        self.Readings['U(V)'] = array([volts])
        self.Readings['I(A)'] = array([amperes])
        #wats = self._get_wats()
        #self.Readings = array([wats])
        measurement_error = 0
        return measurement_error
    def _get_volts(self):
        self.Bus.write_string(('VO?'))
        sleep(self.sleeptime)
        voltage = self.Bus.read_string()
        voltage = voltage.strip('V')
        return float(voltage)
    def set_volts(self, voltage):
        cmdString = ('V %f' % voltage)
        self.Bus.write_string( cmdString)
        return
    def _get_amperes(self):
        self.Bus.write_string(('IO?'))
        sleep(self.sleeptime)
        amperes = self.Bus.read_string()
        amperes = amperes.strip('A')
        return float(amperes)
    def get_amperes_limit(self):
        cmdString = ('I?')
        self.Bus.write_string(cmdString)
        sleep(self.sleeptime)
        amperes = self.Bus.read_string()
        print amperes
        amperes = amperes.strip('I')
        return float(amperes)
    def set_amperes_limit(self, amperes):
        cmdString = ('I %f' % amperes)
        self.Bus.write_string(cmdString)
        return
    def _get_wats(self):
        self.Bus.write_string(('POWER?'))
        sleep(self.sleeptime)
        wats = self.Bus.read_string()
        wats = wats.strip('W')
        return float(wats)
    def set_output_on(self):
        self.Bus.write_string(('OP 1' ))
        return
    def set_output_off(self):
        self.Bus.write_string(('OP 0' ))
        return
    def Set(self, value):
        out_of_bounds = 0
        if value <  0: 
            out_of_bounds = 1 
            self.set_volts(0.0)
        elif value > 4.0:        # limit the PELTIER voltage to 4 volts
            out_of_bounds = 2
            self.set_volts(35)
        else:
            self.Bus.write_string(('V %f' % value))
            #self._assert_OPC()
        self.out_of_bounds = out_of_bounds
        return 
