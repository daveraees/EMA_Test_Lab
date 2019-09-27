# major libs imports:
#from threading import BoundedSemaphore
import Gpib
import serial

# Project libs import
#from CommandIssue import DummyBus
from RAISoft.instruments.LocalTimer import LocalTimerClass


#class BUS_semafor:
#    def __init__(self):
#        self.semafor = BoundedSemaphore(value=1)
#        return 
#    def acquire(self):
#        #self.semafor.acquire()
#        #print 'GPIB locked'
#        return
#    def release(self):
#        #self.semafor.release()
#        #print 'GPIB released'
#        return

# the GPIB bus use flag:
#print 'initializing the GPIB semaphore',
#GPIB_semafor = BUS_semafor()
#print GPIB_semafor
    

    
class ASCIIBus:
    """
    Generalized character I/O interface
    uses "file" interface with read and write functions 
    """
    def __init__(self, type, file_type_interface):
        """ attach the object with read() and write() functions """
        self.f = file_type_interface
        self.type = type
        self.timer = LocalTimerClass()
        self.lastCMDstring = ''    # INITIALIZE the last sent command string value
        return
    def write_string(self, message):
        """ dummy method for writing text message (string) to the device """
        pass
        self.lastCMDstring = message
        raise NotImplementedError
    def writelines(self,commandSequenceString):
        for line in commandSequenceString.splitlines():
            self.write_string(line)
        self.lastCMDstring = commandSequenceString
        return
    def read_string(self, timeout=None):
        """ dummy method for reading the message from the device """
        pass
        raise NotImplementedError
    def read_floats(self, timeout=None, separators=' '):
        """reads the device output buffer, converts the reading into 
        list of floats"""
        readings = self.read_string(timeout)
        floatList = []
        for reading in readings.split(separators):
            floatList.append( float(reading) )
        return floatList
    def read_values(self,timeout=None, separators=' '):
        return self.read_floats(timeout, separators)
    def ask_for_values(self,message, timeout=None, separators=' '):
        """combines functions write_string() and read_floats()"""
        self.write_string(message)
        response = self.read_floats(timeout, separators)
        return response
    def Query(self, message, timeout=None):
        self.write_string(message)
        response = self.read_string(timeout)
        return response
    def ident(self):
        """ acquire identification of the device """
        pass
        raise NotImplementedError
    def clear(self):
        pass
        raise NotImplementedError
    


class SERIALBus(ASCIIBus):
    def __init__(self,BUS,Echoed=False,Terminator='\n'):
        ASCIIBus.__init__(self, 'serial', BUS)
        self.timeout = self.f.timeout # store the timeout value in the field  
        self.lastCMDstring = ''
        self.Echoed = Echoed
        self.terminator = Terminator
        return
    def read_string(self, timeout=None):
        """reads the device output buffer
        if it fails, repeat the last command and try read again"""
        reading = ''
        if timeout == None:
            timeout = self.timeout
        self.timer.zeroTimer()
        while timeout > (self.timer.getSinceLastZeroed()):
            inputLength = self.f.inWaiting() 
            if inputLength:
                character = ''
                while not (character == self.terminator):
                    character = self.f.read(1)
                    reading = reading + character
                break
        # now read the rest if there is anything
        #inputLength = self.f.inWaiting() 
        #if inputLength:
        #    reading = reading + self.f.read(inputLength)
        reading = reading.strip('\n\r')
        reading = reading.strip('\r\n')
        return reading
    def write_string(self, message):
        bytes_num = self.f.write(message)
        if self.Echoed:
            self.read_string(0.6)
        self.lastCMDstring = message
        #self.sbr.semafor.release()
        return
    def ident(self):
        """ acquire identification of the device """
        pass
        return str(self.f.port)    # return  identification
    def close(self):
        self.f.close()
        return
    def clear(self):
        self.f.flushInput()
        self.f.flushOutput()
        # make sure there is nothing in the input buffer 
        inputLength = self.f.inWaiting()
        if inputLength:
            selff.read(inputLength)
        return

class GPIBBus(ASCIIBus):
    #class SBRclass:
    #    "GPIB status byte register"
    #    MAV = 16 # message available - HAS SOME TROUBLES - it is common object to ALL GPIBBus devices
    #    MSS = 32 # Master Summary Status summarizes the ESB and MAV bits.
    #    semafor = None
    lastCMDstring = ''
    #sbr = SBRclass()
    timeout = 0.5 # the commnad issuing and reading timeout
    def __init__(self, deviceIBName, MAVmask=16,IfaceReadyMask=2):
        self.f = Gpib.Gpib(deviceIBName)
        #self.sbr.semafor = GPIB_semafor
        #self.sbr.semafor.acquire()
        print deviceIBName, ':clearing the device buffer...'
        self.clear()
        #self.sbr.semafor.release()
        #self.sbr.MAV = MAVmask    # how to detect the reading was don and response is available
        self.MAVmaks = MAVmask    # sets the message available mask
        self.IfaceReadyMask = IfaceReadyMask    # sets the interface ready mask
        self.CMDexec = 2    # command in execution MASK for the status byte
        self.deviceIBName = deviceIBName
        self.timer = LocalTimerClass()
        return
    def write_string(self, message):
        #self.writebuffer.put(str(message))
        #print self.deviceIBName, ':sending:', message
        #self.sbr.semafor.acquire()
        #if not simple:
        # wait for the interface to get ready
        timeout = self.timeout
        self.timer.zeroTimer()
        if self.IfaceReadyMask:
            while timeout > (self.timer.getSinceLastZeroed()):
                rsp = ord(self.f.rsp())
                interface_ready  = rsp & self.IfaceReadyMask
                break
            if interface_ready:
                self.f.write(message)
                self.lastCMDstring = message
            else:
                pass
        else:
            self.f.write(message)
            self.lastCMDstring = message
        #self.sbr.semafor.release()
        return
    def read_string_simple(self):
        """ method for old Keithley devices (Electrometer K617) """
        #print self.deviceIBName,":using simple read() method to read form device's buffer...",
        reading = self.f.read()
        #print 'DONE!'
        return reading
    def read_string(self, timeout=None):
        """reads the device output buffer
        if it fails, repear the last command and try read again"""
        reading = ''
        if timeout == None:
            timeout = self.timeout
        self.timer.zeroTimer()
        while timeout > (self.timer.getSinceLastZeroed()):
            rsp = ord(self.f.rsp())
            #message_available = rsp & self.sbr.MAV
            message_available  = rsp & self.MAVmaks
            if message_available:
                break
        while message_available:      
            #self.sbr.semafor.acquire()
            #print self.deviceIBName,":Attempting to read form device's buffer...",
            try:
                reading = reading + self.f.read()
                #print ' DONE!'
                #self.sbr.semafor.release()
                
            except Gpib.gpib.error:    # repeat the previous command in case of gpib read error
                #self.sbr.semafor.release()
                print 'read error occurred: clearing the dev buffer..%s \n ressending the last command' % self.f.id
                print self.lastCMDstring
                self.f.clear()
                self.writelines(self.lastCMDstring)
                reading = self.read_string(timeout) # recurrently call the CMD aggain
            rsp = ord(self.f.rsp())
            message_available  = rsp & self.MAVmaks
            #message_available = rsp & self.sbr.MAV # works NOT WELL - it is hared between the GPIBBus devices
        if reading=='':
            reading = '-1e+999'    # this marks error reading
            self.clear()    # clear the instrument bus after the problem
        # self.OUTqueue.put(self.reading)
        reading.strip('\n')
        return reading.strip('\n')
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
    def ident(self):
        self.Bus.write_string('*IDN?')
        self.timer.Wait(0.2)
        return self.read_string()
    def readBinary(self,lengthBytes):
        reading = self.f.readbin(lengthBytes)
        return reading