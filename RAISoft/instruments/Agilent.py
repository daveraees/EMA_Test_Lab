from DummyMeter import Bedna
from numpy import array, hstack, linspace, fromstring, int8, float64
from time import sleep


from RAISoft.Output.OutputFile import OutputFileHandler


class A34401(Bedna):
    def __init__(self, BUS,initSequence=[]):
        Bedna.__init__(self, BUS)
        self.dev.initSequence = initSequence
        self.init()
        unit = self.QueryUnits()
        self.Readings[unit] = array([])
        return
    def QueryUnits(self):
        self.Bus.write_string('FUNC?')
        reading = self.Bus.read_string()
        reading = reading.strip('\n').strip('"')
        return reading
    def Measure(self):
        #self.write_string('INIT')
        #self.write_string('FETCH?')
        self.Bus.writelines('INIT \n FETCH?')
        #self.Bus.write_string('FETCH?')
        reading = self.Bus.read_string()
        Units = self.Readings.keys()
        for unit in Units:
            self.Readings[unit] = array([float(reading)])
        measurement_error = 0
        return measurement_error

class A34401_4ohm(A34401):
    def __init__(self, BUS):
        A34401.__init__(self, BUS,initSequence=['SENS:FUNC "FRES"'])
        self.Readings = {'ohm4(V)':array([])}
        return
    
class A34401_volt(A34401):
    def __init__(self, BUS):
        initSequence = ['SENS:FUNC "VOLT:DC"']
        A34401.__init__(self, BUS,initSequence)
        self.Readings = {'voltT(V)':array([])}
        return

class A34401_HAMAMATSU(A34401):
    def __init__(self, BUS):
        initSequence = ['SENS:FUNC "VOLT:DC"']
        A34401.__init__(self, BUS,initSequence)
        self.Readings = {'HamamatsuLight(V)':array([])}
        return


class A34401_curr(A34401):
    def __init__(self, BUS):
        initSequence = ['SENS:FUNC "CURR:DC"']
        A34401.__init__(self, BUS,initSequence)
        self.Readings = {'CurrentAgilent(A)':array([])}
        return

class A34401_temp(A34401):
    def __init__(self, BUS):
        self.dev.initSequence = ['SENS:FUNC "VOLT:DC"']
        A34401.__init__(self, BUS,initSequence)
        self.Readings = {'Temp(degC)':array([])}
        return
    def Measure(self):
        #self.write_string('INIT')
        #self.write_string('FETCH?')
        self.Bus.writelines('INIT \n FETCH?')
        #self.Bus.write_string('FETCH?')
        reading = self.Bus.read_string()
        Units = self.Readings.keys()
        for unit in Units:
            self.Readings[unit] = array([float(reading)*1000])
        measurement_error = 0
        return measurement_error

class A34401_Pt100(A34401):
    def __init__(self, BUS):
        initSequence = ['SENS:FUNC "FRES"']
        A34401.__init__(self, BUS,initSequence)
        self.Readings = {'Pt100(degC)':array([]),
                         'Pt100ohm4(V)':array([])}
        self.calibration = 0.385 # temperature / resistance coeficient standard
        self.offset = 100 # resistance in ohms at 0 deg.C
        return
    def Measure(self):
        #self.write_string('INIT')
        #self.write_string('FETCH?')
        self.Bus.writelines('INIT \n FETCH?')
        #self.Bus.write_string('FETCH?')
        resistance = float(self.Bus.read_string())
        self.Readings['Pt100ohm4(V)'] = array([resistance])
        # calculate the temperature
        temperature = (resistance - self.offset)/ self.calibration
        self.Readings['Pt100(degC)'] = array([temperature])
        measurement_error = 0
        return measurement_error


class A33220_sinusoid(Bedna):
    def __init__(self, BUS):
        Bedna.__init__(self, BUS)
        self.dev.initSequence = ['*RST',
                                 'FUNC SIN',
                                 'OUTPUT:SYNC ON',
                                 'VOLT:UNIT VRMS']
        self.init()
        self.Readings = {'FreqAgilent(Hz)':array([]),
                         'AmplitudeAgilent(VRMS)':array([]),
                         'OffsetAgilent(Vdc)':array([])}
        return
    def set_freq(self,frequency):
        self.Bus.write_string('FREQ %8.3e' % frequency)
        return
    def get_freq(self):
        freq = self.Bus.ask_for_values('FREQ?')[0]
        return freq
    def set_amplitude_vrms(self,amplitude):
        self.Bus.write_string('VOLT %8.3e' % amplitude)
        return
    def get_amplitude_vrms(self):
        amplitude = self.Bus.ask_for_values('VOLT?')[0]
        return amplitude
    def set_offset(self,DCoffset):
        self.Bus.write_string('VOLT:OFFS %8.3e' % DCoffset)
        return
    def get_offset(self):
        offset = self.Bus.ask_for_values('VOLT:OFFS?')[0]
        return offset
    def set_output_on(self):
        self.Bus.write_string('OUTPUT ON')
        return
    def set_output_off(self):
        self.Bus.write_string('OUTPUT OFF')
        return
    def get_output(self):
        answer = self.Bus.Query('OUTPUT?')
        output = False
        if answer == '1':
            output = True
        if answer == '0':
            output = False            
        return output
    def Measure(self):
        output = self.Bus.Query('APPLY?')
        floats = output.strip('"')[4:]
        list_of_numbers = floats.split(',')
        freq = float(list_of_numbers[0])
        amplitude = float(list_of_numbers[1])
        offset = float(list_of_numbers[2])
        self.Readings['FreqAgilent(Hz)'] = array([freq])
        self.Readings['AmplitudeAgilent(VRMS)'] = array([amplitude])
        self.Readings['OffsetAgilent(Vdc)'] = array([offset])
        measurement_error = 0
        return measurement_error
    
class A33220_square(A33220_sinusoid,Bedna):
    def __init__(self, BUS):
        Bedna.__init__(self, BUS)
        self.dev.initSequence = ['*RST',
                                 'FUNC SQU',
                                 'OUTPUT:SYNC ON',
                                 'VOLT:UNIT VPP']
        self.init()
        self.Readings = {'FreqAgilent(Hz)':array([]),
                         'AmplitudeAgilent(VPP)':array([]),
                         'OffsetAgilent(Vdc)':array([])}
        self.set_duty_cycle(50.0)
        return
    def set_freq(self,frequency):
        self.Bus.write_string('FREQ %8.3e' % frequency)
        return
    def get_freq(self):
        freq = self.Bus.ask_for_values('FREQ?')[0]
        return freq
    def set_duty_cycle(self,percent):
        self.Bus.write_string('FUNC:SQU:DCYC %8.3f' % percent)
        return
    def get_duty_cycle(self):
        percent = self.Bus.ask_for_values('FUNC:SQU:DCYC?')[0]
        return percent
    def set_amplitude_vrms(self,amplitude):
        self.Bus.write_string('VOLT %8.3e' % amplitude)
        return
    def get_amplitude_vrms(self):
        amplitude = self.Bus.ask_for_values('VOLT?')[0]
        return amplitude
    def Measure(self):
        output = self.Bus.Query('APPLY?')
        floats = output.strip('"')[4:]
        list_of_numbers = floats.split(',')
        freq = float(list_of_numbers[0])
        amplitude = float(list_of_numbers[1])
        offset = float(list_of_numbers[2])
        self.Readings['FreqAgilent(Hz)'] = array([freq])
        self.Readings['AmplitudeAgilent(VPP)'] = array([amplitude])
        self.Readings['OffsetAgilent(Vdc)'] = array([offset])
        measurement_error = 0
        return measurement_error
    
    
class A54641A_Scope(Bedna):
    def __init__(self,BUS):
        Bedna.__init__(self, BUS)
        self.dev.initSequence = [":WAV:FORM BYTE",
                                 ":WAV:BYT LSBF",
                                 ":WAV:UNS 0"
                                 ]
        self.init()
        self.Readings = {'Timebase(s)':array([]),
                         'Signal(V)':array([])
                         }
        #self.fileHandler = OutputFileHandler()
        self.set_channel(1)
        self.set_points(1000)
        return
    def _get_preamble(self):
        preamble = {} # format of the osciloscope waveform data
        self.Bus.write_string(":WAV:PRE?")
        response = self.Bus.read_values(separators=',')
        preamble['format'] = int(response[0])
        preamble['type'] = int(response[1])
        preamble['points'] = int(response[2])
        preamble['count'] = int(response[3])
        preamble['xincrement'] = response[4]
        preamble['xorigin'] = response[5]
        preamble['xreference'] = response[6]
        preamble['yincrement'] = response[7]
        preamble['yorigin'] = response[8]
        preamble['yreference'] = response[9]
        return preamble
    def set_trigger(self):
        return
    def get_points(self):
        points = self.points
        return points
    def set_points(self,points):
        self.Bus.write_string(':WAV:POIN %d' % points)
        self.points = points
        return
    def get_channel(self):
        channel = self.channel
        return
    def set_channel(self,channel):
        self.Bus.write_string(':WAV:SOUR CHAN%d' % channel)
        self.channel = channel
        return
    def get_waveform(self,points,channel):
        """
        downloads the waveform data from the osciloscope and 
        calculates the 2 collumns of data
        """
        # set the source and resolution
        self.set_channel(channel)
        self.set_points(points)
        
        # get the formating parameters
        preamble = self._get_preamble()
        points = preamble['points']
        # obtain the RAW data from the 
        self.Bus.write_string(':WAV:DATA?')
        #blockSize = 4096
        header = self.Bus.readBinary(1)
        if header == '#':
            formatLength = int(self.Bus.readBinary(1))
            #print formatLength
            dataLength = int(self.Bus.readBinary(formatLength))
            #print "length of transmission:", dataLength
            #
            #blocks = int (dataLength / blockSize)
            #for block in range(blocks+1):
            #    dataBlock =  self.Bus.readBinary(blockSize)
            #    print "received Bytes:", (block+1)*blockSize
            dataBlock =  self.Bus.readBinary(dataLength)
        else:
            print "wrong file header", header
        
        rawData = fromstring(dataBlock, dtype=int8, count=-1, sep='')
        
        # format the waveform xy data
        
        # construct the time array
        xFrom = preamble['xorigin']
        xTo = preamble['xorigin'] + (preamble['points'] -1)* preamble['xincrement']
        points =  (preamble['points']  )
        xData = linspace(xFrom,xTo,points)
        
        # calculate the measured voltages:
        scale = preamble['yincrement']
        offset = preamble['yorigin']
        yData = rawData * scale + offset
        
        #yData = array([],dtype=float64)
        waveform = {}
        waveform['Timebase(s)'] = xData
        waveform['Signal(V)'] = yData
        return waveform
    def Measure(self):
        waveform = self.get_waveform(points, channel)
    def trigger(self):
        return
#    def save_data_to_file(self,counter,filename):
#        dataFile = open() 
#        return
#    