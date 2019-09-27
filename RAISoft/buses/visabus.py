# major libs imports:
from threading import BoundedSemaphore
from visa import GpibInstrument,SerialInstrument

# Project libs import
#from CommandIssue import DummyBus
from RAISoft.instruments.LocalTimer import LocalTimerClass

class VISABus:
    "implements general functions of the VISA interface"
    timeout = 5.1 # the commnad issuing and readign timeout
    def __init__(self, VISAresourceName):
        self.timer = LocalTimerClass()
        self.deviceIBName = VISAresourceName
        return
    def write_string(self, message):
        #print self.deviceIBName, ':sending:', message
        #self.sbr.semafor.acquire()
        self.f.write(message)
        self.lastCMDstring = message
        #self.sbr.semafor.release()
        return
    def writelines(self,commandSequenceString):
        for line in commandSequenceString.splitlines():
            self.write_string(line)
        self.lastCMDstring = commandSequenceString
        return
    def read_string_simple(self):
        """ method for old Keithley devices (Electrometer K617) """
        print self.deviceIBName,":using simple read() method to read form device's buffer...",
        reading = self.f.read()
        print 'DONE!'
        return reading
    def read_string(self, timeout=None):
        """reads the device output buffer
        if it fails, repear the last command and try read again"""
        reading = ''
        if timeout == None:
            timeout = self.timeout
        self.timer.zeroTimer()
        try:
            #self.f.wait_for_srq(timeout)
            reading = self.f.read()
        except: 
            #self.sbr.semafor.release()
            print 'read error occurred: clearing the dev buffer..\n ressending the last command'
            try:
                self.f.clear()
            except:
                pass
            self.writelines(self.lastCMDstring)
            reading = self.read_string(timeout) # recurrently call the CMD aggain
        
        #while timeout > (self.timer.getSinceLastZeroed()):
        #    rsp = ord(self.f.rsp())
        #    #message_available = rsp & self.sbr.MAV
        #    message_available  = rsp & self.MAVmaks
        #    if message_available:
        #        break
        
        if reading=='':
            reading = '-1e+999'    # this marks error reading
            self.f.clear()    # clear the instrument bus after the problem
        
        # self.OUTqueue.put(self.reading)
        reading.strip('\n')
        return reading.strip('\n')
    def read_strings(self, number, timeout):
        "reads a given NUMBER of strings"
        response = []   # list of strings in response
        for row in range(number):
            response.append (self.read_string())
        return response
    def read_values(self, timeout=None):
        """reads the device output buffer
        as numerical values - using VISA function"""
        reading = ''
        if timeout == None:
            timeout = self.timeout
        self.timer.zeroTimer()
        try:
            #self.f.wait_for_srq(timeout)
            reading = self.f.read_values()
            #print "reading:", reading
        except: 
            #self.sbr.semafor.release()
            print 'read error occurred: clearing the dev buffer..\n ressending the last command'
            self.f.clear()
            self.writelines(self.lastCMDstring)
            reading = self.read_values(timeout) # recurrently call the CMD aggain
        
        #while timeout > (self.timer.getSinceLastZeroed()):
        #    rsp = ord(self.f.rsp())
        #    #message_available = rsp & self.sbr.MAV
        #    message_available  = rsp & self.MAVmaks
        #    if message_available:
        #        break
        
        if reading=='':
            reading = '-1e+999'    # this marks error reading
            self.f.clear()    # clear the instrument bus after the problem
            
        return reading
    def read_floats(self, timeout=None, separators=' '):
        """reads the device output buffer, converts 
        the reading into list of floats"""
        readings = self.read_string(timeout)
        floatList = []
        for reading in readings.split(separators):
            floatList.append( float(reading) )
        return floatList
    def ask_for_values(self, command):
        return self.f.ask_for_values(command)
    def clear(self):
        """clears the device buffer"""
        self.f.clear()
        return
    def trigger(self, triggerString=''):
        if triggerString == '':
            self.f.trigger()
        else:
            self.write_string(triggerString)
        return
    def close(self):
        self.f.close()
        return


class GPIBBus(VISABus):
    "implements communication over GPIB bus using VISA framework"
    
    class SBRclass:
        "GPIB status byte register"
        MAV = 16 # message available - HAS SOME TROUBLES - it is common object to ALL GPIBBus devices
        MSS = 32 # Master Summary Status summarizes the ESB and MAV bits.
        semafor = None
    lastCMDstring = ''
    sbr = SBRclass()
    timeout = 5.1 # the commnad issuing and readign timeout
    def __init__(self, GPIBaddr, MAVmask=16,IfaceReadyMask=0):
        deviceIBName = "GPIB0::%d::INSTR" % GPIBaddr
        VISABus.__init__(self, deviceIBName)
        self.f = GpibInstrument(deviceIBName)
        #self.sbr.semafor = GPIB_semafor
        #self.sbr.semafor.acquire()
        print self.deviceIBName, ':clearing the device buffer...'
        self.f.clear()
        #self.sbr.semafor.release()
        #self.sbr.MAV = MAVmask    # how to detect the reading was don and response is available
        self.MAVmaks = MAVmask    # sets the message available mask
        self.IfaceReadyMask = IfaceReadyMask
        return


class SERIALBus(VISABus):
    "implements communication over COM and LPT buses using VISA framework"
    timeout = 5.1 # the commnad issuing and readign timeout
    def __init__(self, PortName,
                 baud_rate, data_bits, stop_bits, parity, term_chars,
                 Echoed, ReportsStatus):
        "PortName = string of VISA resource descriptor or Allias"
        VISABus.__init__(self, PortName)
        self.f = SerialInstrument(PortName, baud_rate=baud_rate, data_bits=data_bits, stop_bits=stop_bits,
                                  parity=parity, term_chars=term_chars)
        #print self.deviceIBName, ':clearing the device buffer...'
        #self.f.clear()
        self.echoed = Echoed # sets whether the transmissions to the device are achoed back to the interface
        self.reportsStatus = ReportsStatus # sets whether the transmissions
        return
    def SendCommandWaitForCompletion(self, commandMessage, timeout=5):
        self.write_string(commandMessage)
        if self.echoed:
            echo = self.read_string()
        if self.reportsStatus:
            status = self.read_string(timeout)
        else:
            status = 0
        return status
    def Query(self, queryMessage, timeout=5):
        self.write_string(queryMessage)
        if self.echoed:
            echo = self.read_string()
        response = self.read_string(timeout)
        if self.reportsStatus:
            status = self.read_string(timeout)
        else:
            status = 0
        return [response, status]
    


