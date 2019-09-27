# this instruments defines the abstract LCR bridge:

# major libs imports:
from numpy import array, linspace, logspace, hstack, append, sin, cos, tan, abs, pi, log10
from time import sleep

#project libs imports:
from DummyMeter import Bedna



class LCRmeter(Bedna):
    def __init__(self, BUS,Params=None):
        Bedna.__init__(self, BUS)
        self.Readings = {'FREQUENCY(Hz)':array([]), 
                         'Z(ohm)':array([]),
                         'THETA(deg)':array([])}
        if Params == None:
            Params = ['CP(F)','RP(ohm)','CS(F)','RS(ohm)','CP-2(nF-2)']
        self._init_params(Params)
        return
    def _init_params(self, Params):
        """only include the requested parameters into the Readings"""
        for key in Params:
            self.Readings[key] = array([])        
        return
    def setFreq(self, frequency):
        pass
        #return impedanceCPLX
        raise NotImplementedError
    def getFreq(self):
        pass
        #return impedanceCPLX
        raise NotImplementedError
    def setACLevelV(self, levelV):
        pass
        #return impedanceCPLX
        raise NotImplementedError
    def getACLevelV(self):
        pass
        #return impedanceCPLX
        raise NotImplementedError
    def getImpedance(self, freq):
        pass
        #return impedanceCPLX
        raise NotImplementedError
        
    def _calculateParameters(self, freq, impedanceCPLX):
        # calculate the requested parameters, add more as necessary:   
        Z = impedanceCPLX[0]
        THETA = impedanceCPLX[1]
        
        Y = 1 / Z
        PHI = -THETA * pi / 180 # recalculation of phase angle
        omega = 2 * pi * freq   # recalc. of the angular frequency
        G = abs( abs( Y ) * cos( PHI ) )
        RP = 1 / G
        B = abs( abs(Y) * sin (PHI))
        CP = B / (omega)
        RS = abs( abs(Z) * cos(-PHI))
        X = abs( abs(Z) * sin(-PHI))
        LS = X / omega
        LP = 1/(omega * B)
        CS = 1/ (omega * X)
        D = abs( cos(-PHI) / sin (-PHI) )
        Q = 1 / D
        rCP2 = 1/(CP*CP)
        
        parameters = {}
        parameters['Z(ohm)'] = array([Z])
        parameters['THETA(deg)'] = array([THETA])
        keys = self.Readings.keys()
        
        if 'CP(F)' in keys:
            parameters['CP(F)'] = array([CP])
        if 'RP(ohm)' in keys:
            parameters['RP(ohm)'] = array([RP])
        if 'B(S)' in keys:
            parameters['G(S)'] = array([G])
        if 'RS(ohm)' in keys:
            parameters['RS(ohm)'] = array([RS])
        if 'X(ohm)' in keys:
            parameters['X(ohm)'] = array([X])
        if 'Y(S)' in keys:
            parameters['Y(S)'] = array([Y])
        if 'LS(H)' in keys:
            parameters['LS(H)'] = array([LS])
        if 'LP(H)' in keys:
            parameters['LP(H)'] = array([LP])
        if 'CS(F)' in keys:
            parameters['CS(F)'] = array([CS])
        if 'D' in keys:
            parameters['D'] = array([D])
        if 'Q' in keys:
            parameters['Q'] = array([Q])
        if 'CP-2(nF-2)' in keys:
            parameters['CP-2(nF-2)'] = array([rCP2])
             
        return parameters
    def Measure(self, fromFreq=None, toFreq=None, number=None):
        for key in self.Readings.keys():    # clear the previous readings
            self.Readings[key] = array([])
        if not fromFreq:    # measure just one point
            frequency = self.getFreq()
            self.Readings['FREQUENCY(Hz)'] = array([frequency])
            impedanceCPLX = self.getImpedance(frequency)
            parameters = self._calculateParameters(frequency, impedanceCPLX)
            self.Readings.update(parameters)
            measurement_error = 0
        else:    # measure logaritmic frequency sweep
            start = log10(fromFreq)
            stop = log10(toFreq)
            frequencyList = logspace(start, stop, number)
            actualFrequencies = array([])
            for frequency in frequencyList:
                self.setFreq(frequency)
                frequency = self.getFreq()
                impedanceCPLX = self.getImpedance(frequency)
                parameters = self._calculateParameters(frequency, impedanceCPLX)
                for key in parameters.keys():
                    self.Readings[key] = hstack([self.Readings[key],parameters[key]])
                actualFrequencies = append(actualFrequencies,frequency)
            self.Readings['FREQUENCY(Hz)'] = actualFrequencies
            measurement_error = 0

class LCRmeterHP(LCRmeter):
    def __init__(self, BUS, Params):
        LCRmeter.__init__(self, BUS, Params)
        
        self.dev.initSequence = [#'*RST',    # put the device in known state
                                 #':SYST:LFR 50', # set line frequency 50 Hz    
                                 ":SENS:FUNC 'FIMP'",
                                 ":CALC1:FORM MLIN",
                                 ":CALC2:FORM PHAS",    # set to read only Z and PHASE
                                 ":SENS:FIMP:RANG:AUTO ON", # set measurement autorange ON
                                 ":INIT:CONT ON",    # continuous activation of the trigger system
                                 ":TRIG:SOUR BUS"    # use GPIB triggering of the measuremetn
                                 ]
        #self.init()
        # init the value of averaging
        for command in self.dev.initSequence:
            self.Bus.write_string(command)
            sleep(0.2)
        
        self._init_speed()
        return
    def _init_speed(self):
        
        # init the value of frequency
        frequency = self.getFreq()
        print frequency
        self.Readings['FREQUENCY(Hz)'] = array([frequency])
        #init the value of averaging
        self.Bus.write_string('*WAI')
        sleep(0.1)
        self.Bus.write_string(':SENS:AVER ON')
        sleep(0.1)
        self.Bus.write_string(':SENS:AVER:COUN?')
        sleep(0.1)
        averaging = self.Bus.read_string()
        print averaging
        #if averaging == 'OFF':
        #self.averaging = 1
        #else:
        self.averaging = float(averaging)
        #integration
        self.Bus.write_string(':SENS:FIMP:APER?')
        sleep(0.1)
        speed = float(self.Bus.read_string())
        print speed
        #speeds = {'FAST':1, 'NORMAL':16, 'SLOW':64, 'SLOW2':128}
        self.integration = speed
        return
    def _getReadingTime(self, frequency):
        #frequency = self.Readings['FREQUENCY(Hz)']
        #frequency = frequency[0]
        measTime = self.integration * self.averaging
        #print self.integration, self.averaging
        return measTime
    def _trigger(self):
        self.Bus.write_string('*TRG')
        return
    def setFreq(self, frequency):
        """ Only some frequencies are possible:
        100 Hz, 120Hz, 1kHz, 10kHz, 20kHz, 100kHz
        """
        allowed_frequencies = [100,120, 1000, 10000, 20000, 100000] 
        if frequency in allowed_frequencies:
           self.Bus.writelines((':SOUR:FREQ %(freq)f \n *WAI' % \
                               {'freq':frequency}))

        return
    def getFreq(self):
        self.Bus.write_string(':SOUR:FREQ?')
        sleep(0.1)
        freq = self.Bus.read_string()
        return float(freq)
    def setACLevelV(self, levelV):
        allowed_voltages = [0.02, 0.05, 0.1, 0.25, 0.5, 1.0]
        if levelV in allowed_voltages:
            self.Bus.write_string((':SOUR:VOLT %(level)f' % \
                               {'level':levelV}))
        return
    def getACLevelV(self):
        self.Bus.write_string(':SOUR:VOLT?')
        levelV = self.Bus.read_string()
        return float(levelV)
    def getImpedance(self, freq):
        # measure Z and PHASE:
        impedance = self.Bus.read_floats(timeout=20, separators=',')
        Z = impedance[1]
        THETA = impedance[2]
        impedanceCPLX = (Z,THETA)
        return impedanceCPLX
    
class LCRmeterHIOKI(LCRmeter):
    def __init__(self, BUS, Params):
        LCRmeter.__init__(self, BUS, Params)
        
        self.dev.initSequence = ['HEAD OFF',    # turn the headers of resposnses OFF
                                 'MEAS:ITEM 5,0']    # set to read only Z and PHASE
        #self.readingTime = self._getReadingTime()
        self.init()
        # init the value of averaging
        self._init_speed()
        return
    def _init_speed(self):
        # init the value of averaging
        self.Bus.write_string('AVER?')
        averaging = self.Bus.read_string()
        if averaging == 'OFF':
            self.averaging = 1
        else:
            self.averaging = float(averaging)
        #integration
        self.Bus.write_string('SPEED?')
        speed = self.Bus.read_string()
        speeds = {'FAST':1, 'NORMAL':16, 'SLOW':64, 'SLOW2':128}
        self.integration = speeds[speed]
        return
    def _getReadingTime(self, frequency):
        #frequency = self.Readings['FREQUENCY(Hz)']
        #frequency = frequency[0]
        measTime = self.integration * self.averaging / frequency
        print measTime
        return measTime
    def setFreq(self, frequency):
        self.Bus.writelines(('FREQ %(freq)f \n *WAI' % \
                               {'freq':frequency}))
        return
    def getFreq(self):
        self.Bus.write_string('FREQ?')
        freq = self.Bus.read_string()
        return float(freq)
    def setACLevelV(self, levelV):
        self.Bus.write_string(('LEV:VOLT %(level)f' % \
                               {'level':levelV}))
        return
    def getACLevelV(self, levelV):
        self.Bus.write_string('LEV:VOLT?')
        levelV = self.Bus.read_string()
        return float(levelV)
    def getImpedance(self, freq):
        # measure Z and PHASE:
        self.Bus.write_string('MEAS?')
        sleep(self._getReadingTime(freq))
        impedance = self.Bus.read_floats(timeout=20, separators=',')
        Z = impedance[0]
        THETA = impedance[1]
        impedanceCPLX = (Z,THETA)
        return impedanceCPLX
 
 
