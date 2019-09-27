

# drivers for composite devices

from LCRbridge import LCRmeter
from Agilent import A33220_sinusoid
from SRS import LockInSR830


class LCRmeterLockIn_Agilent(LCRmeter):
    """
    Composite device of 
    Sine waveform generator Agilent 33220A and
    SR830 LockIn amplifier
    
    Purpose: Low frequency Schottky barrier capacitance testing 
    With ability to apply DC bias
    """
    def __init__(self, BUS_LI, BUS_Agilent, Params=None):
        LCRmeter.__init__(self, None, Params)
        self.GeneratorSine = A33220_sinusoid(BUS_Agilent)
        self.LockIn = LockInSR830(BUS_LI)
        self.Readings.update(self.LockIn.Readings)
        self.Readings.update(self.GeneratorSine.Readings)
        self.LockIn.set_internal_reference_off()
        return
    def setFreq(self, frequency):
        self.GeneratorSine.set_freq(frequency)
        return
    def getFreq(self):
        frequency = self.LockIn.get_frequency()
        return frequency
    def setACLevelV(self, levelV):
        self.GeneratorSine.set_amplitude_vrms(levelV)
        return
    def getACLevelV(self):
        voltage = self.GeneratorSine.get_amplitude_vrms()
        return voltage
    def getImpedance(self, freq):
        "returns a complex impedance in a form of list (magnitude Z, phase THETA) "
        
        self.LockIn.Measure()
        self.GeneratorSine.Measure()
        self.Readings.update(self.LockIn.Readings)
        self.Readings.update(self.GeneratorSine.Readings)
        
        Vrms = self.Readings['AmplitudeAgilent(VRMS)'][0]
        Irms = self.Readings['MagnitudeR(VA)'][0]
        THETA = self.Readings['PhasePHI(deg)'][0]
        Z = Vrms/Irms
        impedanceCPLX = (Z,THETA)
              
        return impedanceCPLX
    def setBias(self,DCoffset):
        self.GeneratorSine.set_offset(DCoffset)
        return
    def getBias(self):
        DCoffset = self.GeneratorSine.get_offset()
        return DCoffset
    def set_output_on(self):
        self.GeneratorSine.set_output_on()
        return
    def set_output_off(self):
        self.GeneratorSine.set_output_off()
        return
    def auto_gain(self):
        self.LockIn.auto_gain()
        return
    def Close(self):
        self.LockIn.Close()
        self.GeneratorSine.Close()
        return
    

class LCRmeterLockIn(LCRmeter):
    """
    Composite device of 
    Sine waveform generator: Internal harmonic source of LockIn
    SR830 LockIn amplifier
    
    Purpose: Low frequency impedance spectra testing 
    With ability to apply DC bias
    """
    def __init__(self, BUS_LI, Params=None):
        LCRmeter.__init__(self, None, Params)
        self.LockIn = LockInSR830(BUS_LI)
        self.Readings.update(self.LockIn.Readings)
        self.LockIn.set_internal_reference_on()
        return
    def setFreq(self, frequency):
        self.LockIn.set_frequency(frequency)
        return
    def getFreq(self):
        frequency = self.LockIn.get_frequency()
        return frequency
    def setACLevelV(self, levelV):
        self.LockIn.set_sine_amplitude(levelV)
        return
    def getACLevelV(self):
        voltage = self.LockIn.set_sine_amplitude()
        return voltage
    def getImpedance(self, freq):
        "returns a complex impedance in a form of list (magnitude Z, phase THETA) "
        
        self.LockIn.Measure()
        self.Readings.update(self.LockIn.Readings)
        
        Vrms = self.Readings['MagnitudeInternal(V)'][0]
        Irms = self.Readings['MagnitudeR(VA)'][0]
        THETA = self.Readings['PhasePHI(deg)'][0]
        Z = Vrms/Irms
        impedanceCPLX = (Z,THETA)
              
        return impedanceCPLX
    def auto_gain(self):
        self.LockIn.auto_gain()
        return
    def Close(self):
        self.LockIn.Close()
        return