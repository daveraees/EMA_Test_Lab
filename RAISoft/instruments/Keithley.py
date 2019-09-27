# This defines the dual Source Meter driver


# major libs imports:
from numpy import array, linspace, logspace, log10
from time import sleep

#project libs imports:
from DummyMeter import Bedna


class SM2602_channel(Bedna):
    def __init__(self, BUS, channel='a', NPLC=10):
        self.channel = channel.lower()
        Bedna.__init__(self, BUS)
        self.Readings = {('%sVoltage(V)' % self.channel) : array([]), ('%sCurrent(A)' % self.channel) : array([]),('%sTimestamps(s)' % self.channel) : array([])}    # define the units of the measurement readings
        self.dev.initSequence = [('smu%s.sense = 0' % self.channel ), # 2- wire sensing
                                 ('smu%s.source.autorangev = 1' % self.channel ), # set the voltage source range to AUTO
                                 'beeper.enable = 1',    # enable the device sounds
                                 'format.data = format.ASCII' # set the ASCII data transfer format for "printbuffer" function
                                ]
        self.limitI = 0.100 # limit of the source in amperes
        self.limitV = 40.0  # limit of the voltage source in volts
        self.integrTime = NPLC # number of PLC to integrate the measurement
        self.outputState = False

        self.init()
        self._cfg_source_voltage()
        self._cfg_measure_current()
        return
    def _cfg_source_voltage(self):
        self.Bus.write_string(('smu%(channel)s.source.func = smu%(channel)s.OUTPUT_DCVOLTS' % \
                           {'channel':self.channel,}))
        self.set_amperes_limit(self.limitI) # sets the limit of source
        self.outputState = self.get_output_state()
        if not self.outputState:
            self.set_volts(0)    # return the output to zero
            self.set_output_on() # switch on the source output
        return
    def _cfg_measure_current(self):
        self.Bus.write_string(('smu%(ch)s.measure.nplc = %(PLC)u' % \
                           {'ch':self.channel, 'PLC':self.integrTime } )) # set the integration time to 50 PLC
        return
    def get_amperes(self):
        self.Bus.writelines(('reading%(ch)s = smu%(ch)s.measure.i() \n print(reading%(ch)s) ' % \
                           {'ch':self.channel,}))
        reading = self.Bus.read_string(timeout=(0.02*self.integrTime+1.0))
        return float(reading)
    def get_volts(self):
        self.Bus.writelines(('reading%(ch)s = smu%(ch)s.measure.v() \n print(reading%(ch)s) ' % \
                           {'ch':self.channel,}))
        reading = self.Bus.read_string(timeout=(0.02*self.integrTime+1.0))
        return float(reading)
    #def get_iv(self):
    def Measure(self):    
        amperes = self.get_amperes()
        volts = self.get_volts()
        self.Readings[('%sVoltage(V)' % self.channel)] = array([volts])
        self.Readings[('%sCurrent(A)' % self.channel)] = array([amperes])
        self.Readings[('%sTimestamps(s)' % self.channel)] = array([0.0])
        measurement_error = 0
        return measurement_error
    def MeasureIListV(self,voltages,settle_time=0.1):
        """
        Start an TSP built in script for applying an arbitrary list of voltages and measure current
        advantage is in more precise timing in fast scans, 
        than that achieved by external scripting
        """
        numberOfPoints = len(voltages)
        estimated_time = settle_time * numberOfPoints + (self.integrTime * numberOfPoints / 50.0)
        timeout=10
        # instruct the instrument to make a list of tested voltages:
        myVoltages = 'myVoltages = {%.2E' % voltages[0]
        for voltage in voltages[1:]:
            myVoltages = ('%(myVoltages)s, %(voltage).2E' % {'myVoltages':myVoltages ,'voltage':voltage})
        myVoltages = ('%s}' % myVoltages )
        self.Bus.write_string(myVoltages)
        
        command = ('SweepVListMeasureI(smu%(chan)s, myVoltages, %(settle_time)f, %(points)u)' % \
                       {'chan':self.channel, 'settle_time':settle_time, 'points':numberOfPoints} ) 
        self.Bus.write_string(command)
        # wait for completion of the measurement
        command = 'waitcomplete()'
        self.Bus.write_string(command)
        if estimated_time > (timeout-2):
                sleep(estimated_time)
        # read the measured current values
        command = ('printbuffer(1, %(points)u, smu%(chan)s.nvbuffer1.readings)' % \
                       {'chan':self.channel, 'points':numberOfPoints} )
        self.Bus.write_string(command)
        amperes = self.Bus.read_floats(timeout, separators=', ')
        # read the measured voltage values
        command = ('printbuffer(1, %(points)u, smu%(chan)s.nvbuffer1.sourcevalues)' % \
                       {'chan':self.channel, 'points':numberOfPoints} )
        self.Bus.write_string(command)
        voltagesMeasured = self.Bus.read_floats(timeout, separators=', ')
        command = ('printbuffer(1, %(points)u, smu%(chan)s.nvbuffer1.timestamps)' % \
                       {'chan':self.channel, 'points':numberOfPoints} )
        self.Bus.write_string(command)
        timestamps = self.Bus.read_floats(timeout, separators=', ')
        
        self.Readings[('%sVoltage(V)' % self.channel)] = array(voltagesMeasured)
        self.Readings[('%sCurrent(A)' % self.channel)] = array(amperes)
        self.Readings[('%sTimestamps(s)' % self.channel)] = array(timestamps)
        
        measurement_error = 0
        return measurement_error
    def MeasureISweepV(self, start, stop, number, delay, logaritmic=False):
        """
        Start an TSP built in script for applying a voltage ramp and measure current
        advantage is in more precise timing in fast scans, 
        than that achieved by external scripting
        """
        estimated_time = delay * number + (self.integrTime * number / 50.0)
        timeout=10    # for reading the measurement resulta after the finished loop
        if logaritmic:    # the spacing sould be LOGARITMIC
            command = ('SweepVLogMeasureI(smu%(chan)s, %(start)f, %(stop)f, %(delay)f, %(points)u)' % \
                       {'chan':self.channel, 'start':start, 'stop':stop, 'delay':delay, 'points':number} ) 
            self.Bus.write_string(command)
            start = log10(start)
            stop = log10(stop)
            volts = logspace(start, stop, number)
            command = 'waitcomplete()'
            self.Bus.write_string(command)
        else:    # THE spacing sould be LINEAR
            command = ('SweepVLinMeasureI(smu%(chan)s, %(start)f, %(stop)f, %(delay)f, %(points)u)' % \
                       {'chan':self.channel, 'start':start, 'stop':stop, 'delay':delay, 'points':number} ) 
            self.Bus.write_string(command)
            command = 'waitcomplete()'
            self.Bus.write_string(command)
            volts = linspace(start, stop, number)
        if estimated_time > (timeout-2):
                sleep(estimated_time)
        command = ('printbuffer(1, %(points)u, smu%(chan)s.nvbuffer1.readings)' % \
                       {'chan':self.channel, 'points':number} )
        self.Bus.write_string(command)
        amperes = self.Bus.read_floats(timeout, separators=', ')
        # read the measured voltage values
        command = ('printbuffer(1, %(points)u, smu%(chan)s.nvbuffer1.sourcevalues)' % \
                       {'chan':self.channel, 'points':number} )
        self.Bus.write_string(command)
        voltagesMeasured = self.Bus.read_floats(timeout, separators=', ')
        command = ('printbuffer(1, %(points)u, smu%(chan)s.nvbuffer1.timestamps)' % \
                       {'chan':self.channel, 'points':number} )
        self.Bus.write_string(command)
        
        timestamps = self.Bus.read_floats(timeout, separators=', ')
        self.Readings[('%sVoltage(V)' % self.channel)] = array(voltagesMeasured)
        self.Readings[('%sCurrent(A)' % self.channel)] = array(amperes)
        self.Readings[('%sTimestamps(s)' % self.channel)] = array(timestamps)
        
        measurement_error = 0
        return measurement_error 
    def set_volts(self, voltage):
        self.Bus.write_string(('smu%(ch)s.source.levelv = %(volts)f' % \
                           {'ch':self.channel,'volts':voltage} )) # set the output voltage
        return
    def set_amperes_limit(self, amperes):
        self.Bus.write_string(('smu%(ch)s.source.limiti = %(amps)f' % \
                           {'ch':self.channel, 'amps':amperes} )) # set the output current limitation (for voltage sourcing
        return
    def set_output_on(self):
        self.Bus.write_string(('smu%s.source.output = 1' % self.channel))  # sets the output state ON
        return
    def set_output_off(self):
        self.Bus.write_string(('smu%s.source.output = 0' % self.channel))  # sets the output state OFF
        return
    def get_output_state(self):
        self.Bus.writelines(('state%(ch)s = smu%(ch)s.source.output \n print(state%(ch)s) ' % \
                           {'ch':self.channel,}))
        state = self.Bus.read_string()
        stateFloat = float(state)
        if stateFloat == 0:
            output = False
        else:
            output = True
        return output
    def beep(self):
        duration = 0.1    # in seconds
        frequency = 2400  # in Hz
        self.Bus.writelines('beeper.beep(0.1,2400) \n beeper.beep(0.1,1200) \n beeper.beep(0.1,2400)')
        return


class SM2602_FET(Bedna):
    def __init__(self, BUS, NPLC=10):
        Bedna.__init__(self, BUS)
        self.integrTime = NPLC # number of PLC to integrate the measurement
        self.outputState = False
        self.limitI = 0.100 # limit of the source in amperes
        self.limitV = 40.0  # limit of the voltage source in volts
        
        self.Readings = {'sdVoltage(V)' : array([]), 'sdCurrent(A)' : array([]),'sdTimestamps(s)' : array([]),
                         'gVoltage(V)' : array([]), 'gCurrent(A)' : array([]),'gTimestamps(s)' : array([])}    # define the units of the measurement readings
        self.dev.initSequence = ['smua.sense = 0', # 2- wire sensing
                                 'smub.sense = 0' , # 2- wire sensing
                                 'smua.source.autorangev = 1', # set the voltage source range to AUTO
                                 'smub.source.autorangev = 1', # set the voltage source range to AUTO
                                 'smua.source.func = smua.OUTPUT_DCVOLTS',
                                 'smub.source.func = smub.OUTPUT_DCVOLTS',
                                 ('smua.measure.nplc = %(PLC)u' % {'PLC':self.integrTime } ),
                                 ('smub.measure.nplc = %(PLC)u' % {'PLC':self.integrTime } ),
                                 'beeper.enable = 1',    # enable the device sounds
                                 'format.data = format.SREAL', # set the ASCII data transfer format for "printbuffer" function
                                 ]
        
        self.init()
        self._cfg_transistor()
        return
    def cfg_measure_current_integration_time(self, NPLC=None):
        if NPLC == None:
            NPLC = self.integrTime
        self.Bus.write_string(('smua.measure.nplc = %(PLC)u' % \
                           {'PLC':NPLC } )) # set the integration time to 50 PLC
        self.Bus.write_string(('smub.measure.nplc = %(PLC)u' % \
                           {'PLC':NPLC } )) # set the integration time to 50 PLC
        self.integrTime = NPLC
        return
    def _cfg_transistor(self):
        TSPscript = """loadandrunscript Transistor
function OutputChannelAGateB(vlistA, stimeA, pointsA)
    -- Default settings.
    Channel = smua
    Gate = smub
   -- Save settings in temporary variables so they can be restored at the end.
    local l_s_levelv = Channel.source.levelv 
    local l_s_rangev = Channel.source.rangev
    local l_s_autorangev = Channel.source.autorangev 
    local l_s_func = Channel.source.func
    local l_m_autozero = Channel.measure.autozero
    local l_d_screen = display.screen
    local gate_output = Gate.source.output
   -- Temporary variables used by this function.
    local l_j
   -- Clear the front panel display then prompt for input parameters if missing.
    display.clear()  
    if pointsA == nil then
        pointsA = display.prompt("0000", " Points", "Enter number of Source-Drain sweep POINTS.", 10, 1, 1000)    
        if pointsA == nil then
            --Abort if Exit key pressed
            AbortScript(l_d_screen)
        end
    end
    if stimeA == nil then
        stimeA = display.prompt("+0.000E+00", " Seconds", "Enter SETTLING time for Source-Drain.", 0, 0, 10)
        if stimeA == nil then
            --Abort if Exit key pressed
            AbortScript(l_d_screen)
        end
    end
    if vlistA == nil then
        vlistA = {}
        for l_j = 1,pointsA do
            vlistA[l_j] = display.prompt("+00.000", " Volts", "Enter Source-Drain voltage "..string.format("%d",l_j), -1, -40, 40)        
            if  vlistA[l_j] == nil then
                --Abort if Exit key pressed
                AbortScript(l_d_screen)
            end
        end
    end
        display.clear()      
   -- Update display with test info.
    display.settext("FET OutputChanAGateB")  -- Line 1 (20 characters max)
   -- Configure source and measure settings.
    Channel.source.output = Channel.OUTPUT_OFF
    Channel.source.func = Channel.OUTPUT_DCVOLTS
    Channel.source.autorangev = Channel.AUTORANGE_ON
    Channel.source.levelv = vlistA[1]
    Channel.measure.autozero = Channel.AUTOZERO_OFF
   -- Setup a buffer to store the result(s) in and start testing of the Source-drain channel.
    Channelbuffer = Channel.makebuffer(pointsA)
    Channelbuffer.clear()
    Channelbuffer.appendmode = 1
    Channelbuffer.collecttimestamps = 1
    Channelbuffer.collectsourcevalues = 1
   -- Setup a buffer to store the result(s) in and start testing of the Source-drain channel.
    Gatebuffer = Gate.makebuffer(pointsA)
    Gatebuffer.clear()
    Gatebuffer.appendmode = 1
    Gatebuffer.collecttimestamps = 1
    Gatebuffer.collectsourcevalues = 1
   -- Apply the voltage to the Source-gate and wait specified time
    gate_output = Gate.source.levelv
    display.setcursor(2,1)             
    display.settext("GateB voltage: "..string.format("%f",gate_output))      -- Line 2 (32 characters max)
   -- Apply the voltage to the Source-drain channel 
    Channel.source.output = Channel.OUTPUT_ON
    for l_j = 1,pointsA do
        Channel.source.levelv = vlistA[l_j]  -- Program source to sweep level.
        display.setcursor(2,1)             
        display.settext("ChannelA voltage: "..string.format("%f",vlistA[l_j]))      -- Line 2 (32 characters max)
        delay(stimeA)                    -- Wait desired settling time.
        Channel.measure.overlappedi(Channelbuffer)    -- Measure Source-Drain current and store in reading buffer.
        Gate.measure.overlappedi(Gatebuffer)    -- Measure Source-Gate current and store in reading buffer.
        waitcomplete()
    end
    Channel.source.output = Channel.OUTPUT_OFF
   -- Update the front panel display and restore modified settings.
    display.setcursor(2,1)             
    display.settext("Test complete.                  ")      -- Line 2 (32 characters max)
    Channel.source.levelv = l_s_levelv
    Channel.source.func = l_s_func
    Channel.source.autorangev = l_s_autorangev
    Channel.measure.autozero = l_m_autozero
    display.clear()
    display.screen = l_d_screen
end

function TransferChannelAGateB(vlistA, stimeA, pointsA)
    -- Default settings.
    Channel = smua
    Gate = smub
   -- Save settings in temporary variables so they can be restored at the end.
    local l_s_levelv = Gate.source.levelv 
    local l_s_rangev = Gate.source.rangev
    local l_s_autorangev = Gate.source.autorangev 
    local l_s_func = Gate.source.func
    local l_m_autozero = Gate.measure.autozero
    local l_d_screen = display.screen
    local channel_output = Channel.source.output
   -- Temporary variables used by this function.
    local l_j
   -- Clear the front panel display then prompt for input parameters if missing.
    display.clear()  
    if pointsA == nil then
        pointsA = display.prompt("0000", " Points", "Enter number of Source-Drain sweep POINTS.", 10, 1, 1000)    
        if pointsA == nil then
            --Abort if Exit key pressed
            AbortScript(l_d_screen)
        end
    end
    if stimeA == nil then
        stimeA = display.prompt("+0.000E+00", " Seconds", "Enter SETTLING time for Source-Drain.", 0, 0, 10)
        if stimeA == nil then
            --Abort if Exit key pressed
            AbortScript(l_d_screen)
        end
    end
    if vlistA == nil then
        vlistA = {}
        for l_j = 1,pointsA do
            vlistA[l_j] = display.prompt("+00.000", " Volts", "Enter Source-Drain voltage "..string.format("%d",l_j), -1, -40, 40)        
            if  vlistA[l_j] == nil then
                --Abort if Exit key pressed
                AbortScript(l_d_screen)
            end
        end
    end
        display.clear()      
   -- Update display with test info.
    display.settext("FET TransferChanAGateB")  -- Line 1 (20 characters max)
   -- Configure source and measure settings.
    Gate.source.output = Channel.OUTPUT_OFF
    Gate.source.func = Channel.OUTPUT_DCVOLTS
    Gate.source.autorangev = Channel.AUTORANGE_ON
    Gate.source.levelv = vlistA[1]
    Gate.measure.autozero = Channel.AUTOZERO_OFF
   -- Setup a buffer to store the result(s) in and start testing of the Source-drain channel.
    Channelbuffer = Channel.makebuffer(pointsA)
    Channelbuffer.clear()
    Channelbuffer.appendmode = 1
    Channelbuffer.collecttimestamps = 1
    Channelbuffer.collectsourcevalues = 1
   -- Setup a buffer to store the result(s) in and start testing of the Source-drain channel.
    Gatebuffer = Gate.makebuffer(pointsA)
    Gatebuffer.clear()
    Gatebuffer.appendmode = 1
    Gatebuffer.collecttimestamps = 1
    Gatebuffer.collectsourcevalues = 1
   -- Display the voltage on the Source-drain 
    channel_output = Channel.source.levelv
    display.setcursor(2,1)             
    display.settext("ChannelA voltage: "..string.format("%f",channel_output))      -- Line 2 (32 characters max)
   -- Apply the voltage to the Gate-Source  
    Gate.source.output = Gate.OUTPUT_ON
    for l_j = 1,pointsA do
        Gate.source.levelv = vlistA[l_j]  -- Program source to sweep level.
        display.setcursor(2,1)             
        display.settext("GateB voltage: "..string.format("%f",vlistA[l_j]))      -- Line 2 (32 characters max)
        delay(stimeA)                    -- Wait desired settling time.
        Gate.measure.overlappedi(Gatebuffer)    -- Measure Source-Gate current and store in reading buffer.
        Channel.measure.overlappedi(Channelbuffer)    -- Measure Source-Drain current and store in reading buffer.
        waitcomplete()
    end
    Gate.source.output = Gate.OUTPUT_OFF
   -- Update the front panel display and restore modified settings.
    display.setcursor(2,1)             
    display.settext("Test complete.                  ")      -- Line 2 (32 characters max)
    Gate.source.levelv = l_s_levelv
    Gate.source.func = l_s_func
    Gate.source.autorangev = l_s_autorangev
    Gate.measure.autozero = l_m_autozero
    display.clear()
    display.screen = l_d_screen
end
endscript
        """
        self.Bus.writelines(TSPscript)
        return
    
    def get_amperes(self, channel='a'):
        self.Bus.writelines(('reading%(ch)s = smu%(ch)s.measure.i() \n print(reading%(ch)s) ' % \
                           {'ch':channel,}))
        reading = self.Bus.read_string(timeout=(0.02*self.integrTime+1))
        return float(reading)
    def get_volts(self, channel='a'):
        self.Bus.writelines(('reading%(ch)s = smu%(ch)s.measure.v() \n print(reading%(ch)s) ' % \
                           {'ch':channel,}))
        reading = self.Bus.read_string(timeout=(0.02*self.integrTime+1))
        return float(reading)
    #def get_iv(self):
    def Measure(self):    
        amperes = self.get_amperes()
        volts = self.get_volts()
        self.Readings['sdVoltage(V)'] = array([volts])
        self.Readings['sdCurrent(A)'] = array([amperes])
        self.Readings['sdTimestamps(s)'] = array([0.0])
        amperes = self.get_amperes(channel='b')
        volts = self.get_volts(channel='b')
        self.Readings['gVoltage(V)'] = array([volts])
        self.Readings['gCurrent(A)'] = array([amperes])
        self.Readings['gTimestamps(s)'] = array([0.0])
        measurement_error = 0
        return measurement_error
    def Upload_source_drain_voltages(self, voltages):
        myVoltages = 'myVoltages = {%.3f}' % voltages[0]
        self.Bus.write_string(myVoltages)
        for voltage in voltages[1:]:
            addVoltage = ('table.insert(myVoltages, %(voltage).3f )' % {'voltage':voltage})
            self.Bus.write_string(addVoltage)
        numberOfPoints = len(voltages)
        self.Bus.write_string('numberOfPoints = %u' % numberOfPoints)
        return numberOfPoints
    def MeasureSweepChannelA(self, SDsettle_time=0.1):
        """
        Start an TSP built in script for applying an arbitrary list of voltages and measure current
        advantage is in more precise timing in fast scans, 
        than that achieved by external scripting
        """
        self.Bus.write_string('printnumber (numberOfPoints)')
        response =  self.Bus.read_bin_floats()
        numberOfPoints = response[0]
        estimated_time = SDsettle_time * numberOfPoints + ( 2 * self.integrTime * numberOfPoints / 50.0)
        timeout=10
        # instruct the instrument to make a list of tested SDvoltages:
        # perform the SD voltage sweep for given Gate voltage
        #OutputChannelAGateB(vlistA, voltageB, stimeA, stimeB, pointsA)
        command = ('OutputChannelAGateB(myVoltages, %(SDsettle_time)f, numberOfPoints)' % \
                       {'SDsettle_time':SDsettle_time} ) 
        self.Bus.write_string(command)
        # wait for completion of the measurement
        command = 'waitcomplete()'
        self.Bus.write_string(command)
        if estimated_time > (timeout-2):
                sleep(estimated_time)
        # read the measured current values
        command = ('printbuffer(1, %(points)u, Channelbuffer.readings)' % \
                       {'points':numberOfPoints} )
        self.Bus.write_string(command)
        amperes = self.Bus.read_bin_floats(timeout)
        # read the measured voltage values
        command = ('printbuffer(1, %(points)u, Channelbuffer.sourcevalues)' % \
                       {'points':numberOfPoints} )
        self.Bus.write_string(command)
        voltagesMeasured = self.Bus.read_bin_floats(timeout)
        command = ('printbuffer(1, %(points)u, Channelbuffer.timestamps)' % \
                       {'points':numberOfPoints} )
        self.Bus.write_string(command)
        timestamps = self.Bus.read_bin_floats(timeout)
        
        self.Readings['sdVoltage(V)'] = array(voltagesMeasured)
        self.Readings['sdCurrent(A)'] = array(amperes)
        self.Readings['sdTimestamps(s)'] = array(timestamps)
        # once again the same for Gate readings
        command = ('printbuffer(1, %(points)u, Gatebuffer.readings)' % \
                       {'points':numberOfPoints} )
        self.Bus.write_string(command)
        amperes = self.Bus.read_bin_floats(timeout)
        # read the measured voltage values
        command = ('printbuffer(1, %(points)u, Gatebuffer.sourcevalues)' % \
                       {'points':numberOfPoints} )
        self.Bus.write_string(command)
        voltagesMeasured = self.Bus.read_bin_floats(timeout)
        command = ('printbuffer(1, %(points)u, Gatebuffer.timestamps)' % \
                       {'points':numberOfPoints} )
        self.Bus.write_string(command)
        timestamps = self.Bus.read_bin_floats(timeout)
        
        self.Readings['gVoltage(V)'] = array(voltagesMeasured)
        self.Readings['gCurrent(A)'] = array(amperes)
        self.Readings['gTimestamps(s)'] = array(timestamps)
        
        measurement_error = 0
        return measurement_error
    def MeasureSweepGateB(self, Gsettle_time=0.1):
        """
        Start an TSP built in script for applying an arbitrary list of voltages and measure current
        advantage is in more precise timing in fast scans, 
        than that achieved by external scripting
        """
        self.Bus.write_string('printnumber (numberOfPoints)')
        response =  self.Bus.read_bin_floats()
        numberOfPoints = response[0]
        estimated_time = Gsettle_time * numberOfPoints + ( 2 * self.integrTime * numberOfPoints / 50.0)
        timeout=10
        # instruct the instrument to make a list of tested SDvoltages:
        # perform the SD voltage sweep for given Gate voltage
        #OutputChannelAGateB(vlistA, voltageB, stimeA, stimeB, pointsA)
        command = ('TransferChannelAGateB(myVoltages, %(Gsettle_time)f, numberOfPoints)' % \
                       {'Gsettle_time':Gsettle_time} ) 
        self.Bus.write_string(command)
        # wait for completion of the measurement
        command = 'waitcomplete()'
        self.Bus.write_string(command)
        if estimated_time > (timeout-2):
                sleep(estimated_time)
        # read the measured current values
        command = ('printbuffer(1, %(points)u, Channelbuffer.readings)' % \
                       {'points':numberOfPoints} )
        self.Bus.write_string(command)
        amperes = self.Bus.read_bin_floats(timeout)
        # read the measured voltage values
        command = ('printbuffer(1, %(points)u, Channelbuffer.sourcevalues)' % \
                       {'points':numberOfPoints} )
        self.Bus.write_string(command)
        voltagesMeasured = self.Bus.read_bin_floats(timeout)
        command = ('printbuffer(1, %(points)u, Channelbuffer.timestamps)' % \
                       {'points':numberOfPoints} )
        self.Bus.write_string(command)
        timestamps = self.Bus.read_bin_floats(timeout)
        
        self.Readings['sdVoltage(V)'] = array(voltagesMeasured)
        self.Readings['sdCurrent(A)'] = array(amperes)
        self.Readings['sdTimestamps(s)'] = array(timestamps)
        # once again the same for Gate readings
        command = ('printbuffer(1, %(points)u, Gatebuffer.readings)' % \
                       {'points':numberOfPoints} )
        self.Bus.write_string(command)
        amperes = self.Bus.read_bin_floats(timeout)
        # read the measured voltage values
        command = ('printbuffer(1, %(points)u, Gatebuffer.sourcevalues)' % \
                       {'points':numberOfPoints} )
        self.Bus.write_string(command)
        voltagesMeasured = self.Bus.read_bin_floats(timeout)
        command = ('printbuffer(1, %(points)u, Gatebuffer.timestamps)' % \
                       {'points':numberOfPoints} )
        self.Bus.write_string(command)
        timestamps = self.Bus.read_bin_floats(timeout)
        
        self.Readings['gVoltage(V)'] = array(voltagesMeasured)
        self.Readings['gCurrent(A)'] = array(amperes)
        self.Readings['gTimestamps(s)'] = array(timestamps)
        
        measurement_error = 0
        return measurement_error
    def set_volts(self, voltage, channel = 'a'):
        self.Bus.write_string(('smu%(ch)s.source.levelv = %(volts)f' % \
                           {'ch':channel,'volts':voltage} )) # set the output voltage
        return
    def set_amperes_limit(self, amperes,channel = 'a'):
        self.Bus.write_string(('smu%(ch)s.source.limiti = %(amps)f' % \
                           {'ch':channel, 'amps':amperes} )) # set the output current limitation (for voltage sourcing
        return
    def set_output_on(self,channel = 'a'):
        self.Bus.write_string(('smu%s.source.output = 1' % channel))  # sets the output state ON
        return
    def set_output_off(self,channel = 'a'):
        self.Bus.write_string(('smu%s.source.output = 0' % channel))  # sets the output state OFF
        return
    def get_output_state(self,channel = 'a'):
        self.Bus.writelines(('state%(ch)s = smu%(ch)s.source.output \n print(state%(ch)s) ' % \
                           {'ch':channel,}))
        state = self.Bus.read_string()
        stateFloat = float(state)
        if stateFloat == 0:
            output = False
        else:
            output = True
        return output
    def beep(self):
        duration = 0.1    # in seconds
        frequency = 2400  # in Hz
        self.Bus.writelines('beeper.beep(0.1,2400) \n beeper.beep(0.1,1200) \n beeper.beep(0.1,2400)')
        return        

class SM2602_4PP(Bedna):
    """
    This can be used for measurement with the linear array four-point-probe
    Channel A is used to measure voltage in the inner pair of the contacts
    Channel B  Sources the current into the outer pair  contacts
    """
    def __init__(self, BUS, NPLC=10):
        Bedna.__init__(self, BUS)
        self.integrTime = NPLC # number of PLC to integrate the measurement
        self.outputState = False
        self.limitI = 0.100 # limit of the source in amperes
        self.limitV = 40.0  # limit of the voltage source in volts
        
        self.Readings = {'4PPVoltage(V)' : array([]), '4PPCurrent(A)' : array([]),'4PPTimestamps(s)' : array([])}    # define the units of the measurement readings
        self.dev.initSequence = ['smua.sense = 0', # 2- wire sensing
                                 'smub.sense = 0' , # 2- wire sensing
                                 'smua.measure.autorangev = 1', # set the voltage source range to AUTO
                                 'smub.measure.autorangei = 1', # set the voltage source range to AUTO
                                 'display.smua.measure.func = display.MEASURE_DCVOLTS',
                                 'display.smub.measure.func = display.MEASURE_DCAMPS',
                                 'smua.source.autorangei = 1', # set the voltage source range to AUTO
                                 'smub.source.autorangei = 1', # set the voltage source range to AUTO
                                 'smua.source.func = smua.OUTPUT_DCAMPS',
                                 'smua.source.leveli = 0', # channel A is used for measurement of the voltage
                                 'smub.source.func = smub.OUTPUT_DCAMPS',
                                 'smub.source.limitv = 40.0',
                                 ('smua.measure.nplc = %(PLC)u' % {'PLC':self.integrTime } ),
                                 ('smub.measure.nplc = %(PLC)u' % {'PLC':self.integrTime } ),
                                 'beeper.enable = 1',    # enable the device sounds
                                 'format.data = format.SREAL', # set the ASCII data transfer format for "printbuffer" function
                                 ]
        
        self.init()
        return
    def get_amperes(self, channel='b'):
        self.Bus.writelines(('reading%(ch)s = smu%(ch)s.measure.i() \n print(reading%(ch)s) ' % \
                           {'ch':channel,}))
        reading = self.Bus.read_string(timeout=(0.02*self.integrTime+1))
        return float(reading)
    def get_volts(self, channel='a'):
        self.Bus.writelines(('reading%(ch)s = smu%(ch)s.measure.v() \n print(reading%(ch)s) ' % \
                           {'ch':channel,}))
        reading = self.Bus.read_string(timeout=(0.02*self.integrTime+1))
        return float(reading)
    #def get_iv(self):
    def Measure(self):    
        amperes = self.get_amperes(channel='b')
        volts = self.get_volts(channel='a')
        self.Readings['4PPVoltage(V)'] = array([volts])
        self.Readings['4PPCurrent(A)'] = array([amperes])
        self.Readings['4PPTimestamps(s)'] = array([0.0])
        measurement_error = 0
        return measurement_error
    def set_amperes(self, amperes, channel = 'b'):
        self.Bus.write_string(('smu%(ch)s.source.leveli = %(amps)e' % \
                           {'ch':channel,'amps':amperes} )) # set the output voltage
        return
    def set_voltage_limit(self, voltage,channel = 'b'):
        self.Bus.write_string(('smu%(ch)s.source.limitv = %(volts)e' % \
                           {'ch':channel, 'volts':voltage} )) # set the output current limitation (for voltage sourcing
        return
    def set_output_on(self,channel = 'a'):
        self.Bus.write_string(('smu%s.source.output = 1' % channel))  # sets the output state ON
        return
    def set_output_off(self,channel = 'a'):
        self.Bus.write_string(('smu%s.source.output = 0' % channel))  # sets the output state OFF
        return
    def get_output_state(self,channel = 'a'):
        self.Bus.writelines(('state%(ch)s = smu%(ch)s.source.output \n print(state%(ch)s) ' % \
                           {'ch':channel,}))
        state = self.Bus.read_string()
        stateFloat = float(state)
        if stateFloat == 0:
            output = False
        else:
            output = True
        return output
    def beep(self):
        duration = 0.1    # in seconds
        frequency = 2400  # in Hz
        self.Bus.writelines('beeper.beep(0.1,2400) \n beeper.beep(0.1,1200) \n beeper.beep(0.1,2400)')
        return        


class Electrometer617(Bedna):
    def __init__(self, BUS):
        Bedna.__init__(self, BUS)
        #GPIBDevice.__init__(self, GPIBName, Identificator='Keithley 617 Electrometer', MAVmask=8)
        self.Readings = {'Volt617(V)': array([]), 'Curr617(A)': array([])}    # define the units of the measurement readings
        self.dev.initSequence = ['F1X', # function: amperes
                                 'Z0N0X', # zero CHECK
                                 'D0X',    # display electrometer
                                 'B0X',    # readings directly from electrometer
                                 'R0X',    # AUTORANGE
                                 'T2X',    # trigger CONTINUOUS on GET
                                 'Q7X',    # data store control OFF
                                 'G1X',    # do NOT send prefix with data
                                 #'X',     # execute the commands
                                 'C1XZ1XC0X' # perform "zero the instrument"
                                 ]
        self.init()
        self.limitI = 0.0019 # limit of the source in amperes
        self.limitV = 102.0  # limit of the voltage source in volts
        self.integrTime = 17 # number of PLC to integrate the measurement 17 = 333ms
        self.outputState = False
        self.actualVoltage = 0.0
        self.zero_check('off')
        self.set_output_on()
        self.Bus.trigger()
        #self.Bus.clear()
        return
    def get_amperes(self):
        """ reads the device measurement result - current"""
        #sleep(0.1)
        try:
            #reading = self.Bus.read_floats(separators='\n')
            #amperes = reading[-1]
            reading = self.Bus.read_string_simple()
            amperes = float(reading)
        except:
            amperes = 0.0
        if amperes > self.limitI:
            self.set_output_off()
            self.zero_check('on')
        return amperes
    def get_volts(self):
        self.Bus.write_string('B4X')
        reading = self.Bus.read_string_simple()
        self.Bus.write_string('B0X')
        #self.Bus.trigger()
        volts = float(reading)
        self.actualVoltage = volts
        return volts
    def set_volts(self, voltage):
        """ sends a command string to immediately set voltage - does the check for limits"""
        if voltage > self.limitV:
            voltage = self.limitV
        if voltage < (-self.limitV):
            voltage = - self.limitV
        command = ('V%(voltage)+2.5EX' % {'voltage':voltage})
        self.Bus.write_string(command)
        #self.actualVoltage = voltage
        return
    def zero_check(self, state=''):
        """ set the zero check ON or OFF"""
        if state == '':
            pass
        else:
            state.lower().strip()
            if state == 'off':
                self.Bus.write_string('C0X')
            if state == 'on':
                self.Bus.write_string('C1X')
        return
    def set_output_on(self):
        self.Bus.write_string('O1X')
        return
    def set_output_off(self):
        self.Bus.write_string('O0X')
        return
    def Measure(self):    
            amperes = self.get_amperes()
            volts = self.get_volts()
            self.Readings['Volt617(V)'] = array([volts])
            self.Readings['Curr617(A)'] = array([amperes])
            measurement_error = 0
            return measurement_error

class Electrometer6517(Bedna):
    def __init__(self, BUS, integrTime=None, identString='',elements = 'READ,TST,ETEM,VSO',units ='A,s,C,V'):
        Bedna.__init__(self, BUS)
        #GPIBDevice.__init__(self, GPIBName, Identificator='Keithley Electrometer model 6517A')
        self.limitI = 0.010 # limit of the source in amperes
        self.limitV = 1000.0  # limit of the voltage source in volts
        self.identString = identString # record the given string of identification of the values in datafile
        if integrTime == None:
           self.integrTime = 5 # number of PLC to integrate the measurement 17 = 333ms
        else:
           self.integrTime = integrTime 
        self.Readings = dict()
        #self.Readings = {'Volt6517(V)': array([]), 'Curr6517(A)': array([]),'Time6517(s)': array([])}    # define the units of the measurement readings
        i=0
        self.elementsNames = []
        self.unitsNames = units.split(',')
        for elem in  elements.split(','):
            ElementFullName = ('%(element)s_%(ident)s(%(unit)s)' % {'element':elem, 'ident':self.identString, 'unit':self.unitsNames[i]})
            self.elementsNames.append(ElementFullName)
            self.Readings[ElementFullName] = array([])
            i+=1
        #{('Volt6517_%s(V)' % self.identString): array([]), ('Curr6517_%s(A)' % self.identString): array([])}    # define the units of the measurement readings
        self.dev.initSequence = [":SYST:PRES",    # resets the system
                                 #"*WAI",
                                 ':SYST:ZCH ON', # zero CHECK
                                 #"*WAI",
                                 ':FUNC "CURR"', # function: amperes
                                 #"*WAI",
                                 #":CURR:RANG 20e-12",
                                 #"*WAI",
                                 #":SYST:ZCOR ON",    # perform zero correction
                                 #"*WAI",
                                 ":CURR:RANG:AUTO ON",    # AUTORANGE
                                 #":SOURCE:VOLTAGE:RANGE 1000", # set voltage source range to 1000 V
                                 #":SOURCE:VOLTAGE:LIMIT 1000", # set voltage source limit to 1000 V
                                 #"*WAI",
                                 (":FORM:ELEM %s" % elements ),    # send just the reading over the BUS
                                 #"*WAI",
                                 (":CURR:NPLC %i" % self.integrTime), # set integration time in powerline cycles
                                 #"*WAI",
                                 ":SYST:TST:TYPE REL",               # sets timestamp type to relative
                                 #":ARM:LAY1:IMM",    # sets Immediate trigerring of layer 1
                                 #":ARM:LAY2:IMM",    # sets Immediate trigerring of layer 2
                                 #":TRIG:IMM",    # sets Immediate trigerring of layer 2
                                 ":INIT:CONT ON",                # sets continuous triggering ON
                                 #':TRIG:SOUR BUS',                   # turns on internal continuous trigger
                                 ':SYST:TSC ON', # enable external temperature measurement
                                 ':DATA:CLE', # clear readings from buffer
                                 ]
        self.init()
        self.outputState = False
        self.actualVoltage = 0.0
        self.zero_check('off')
        #sleep(6.0) # wait for initialization after autorange
        #self.set_output_on()
        #self.Bus.trigger() # in the default setup, the electrometer uses internal trigger
        #self.Bus.clear()
        #self.reset_timestamp()
        return
    def get_amperes(self):
        #self.Bus.write_string(":TRIG:SOUR BUS") # turns off continuous trigger, sets the BUS to trigger the measurements
        """ reads the device measurement result - current"""
        #self.Bus.trigger()
        self.Bus.write_string(':SENS:DATA:FRES?')
        sleep(1.0 / 50.0 * self.integrTime)           # wait during the integration time
        #self.Bus.write_string(":TRIG:SOUR TIM") #
        reading = self.Bus.read_values()
        amperes = reading[0]
        #timestamp = reading[1]
        #rdgCount = reading[2]
        return (amperes)
    def get_volts(self):
        reading = self.Bus.ask_for_values(":SOUR:VOLT:LEV:IMM:AMPL?")
        volts = reading[0]
        self.actualVoltage = volts
        return volts
    def set_volts(self, voltage):
        """ sends a command string to immediately set voltage - does the check for limits"""
        if voltage > self.limitV:
            voltage = self.limitV
        if voltage < (-self.limitV):
            voltage = self.limitV
        response = self.Bus.ask_for_values(":SOUR:VOLT:RANG?", timeout=8)
        # "Autorange the voltage source"
        if (abs(voltage) > response[0]):
           self.Bus.write_string(":SOUR:VOLT:RANG 1000")
        else:
             if (not (response[0]==100) ) and (abs(voltage) < 100):
                self.Bus.write_string(":SOUR:VOLT:RANG 100")
        command = (':SOUR:VOLT:LEV:IMM:AMPL %(voltage)+2.5E' % {'voltage':voltage})
        self.Bus.write_string(command)
        #self.actualVoltage = voltage
        return
    def zero_check(self, state=''):
        """ set the zero check ON or OFF"""
        if state == '':
            pass
        else:
            state.lower().strip()
            if state == 'off':
                self.Bus.write_string(':SYST:ZCH OFF')
                sleep(6.0)
            if state == 'on':
                self.Bus.write_string(':SYST:ZCH ON')
        return
    def set_output_on(self):
        self.Bus.write_string(':SENS:RES:MAN:VSO:OPER ON')
        sleep(1.0 / 50.0 * self.integrTime)
        return
    def set_output_off(self):
        self.Bus.write_string(':SENS:RES:MAN:VSO:OPER OFF')
        sleep(1.0 / 50.0 * self.integrTime)
        return
    def reset_timestamp(self):
        self.Bus.write_string(':SYST:TST:REL:RES')
        sleep(1.0 / 50.0 * self.integrTime)
    def Measure(self):
        #self.Bus.trigger()
        #sleep(1.0 / 50.0 * self.integrTime)
        #self.Bus.trigger()
        self.Bus.write_string(':SENS:DATA:FRES?')
        sleep(1.0 / 50.0 * (self.integrTime+1))           # wait during the integration time
        #self.Bus.write_string(":TRIG:SOUR TIM") #
        readings = self.Bus.read_values(timeout=8, separators=',')
        i = 0
        #print readings
        for elem in  self.elementsNames:
            self.Readings[elem] = array([readings[i]])
            i +=1    
        #self.Readings[('Volt6517_%s(V)' % self.identString)] = array([volts])
        #self.Readings[('Curr6517_%s(A)' % self.identString)] = array([reading])
        #self.Readings['Time6517(s)'] = array([reading[1]])
        measurement_error = 0
        return measurement_error
