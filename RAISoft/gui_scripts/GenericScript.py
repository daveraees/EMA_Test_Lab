# this define the generic properties of the script

import os
import threading

from RAISoft.wxGUI.GuiExceptions import JobTerminationException

from RAISoft.instruments.ActiveDevicesList import ListOfDevices
from RAISoft.instruments.LocalTimer import LocalTimerClass
from RAISoft.instruments.active_devices_list import ListOfDevices
from RAISoft.Output.Output_for_gui import OutputHandler
from Parameter import GeneralParameter


class TestScript:
    """
    this define sthe generic properties of the script
    """
    def __init__(self):
        self.timer = LocalTimerClass()        
        self._parameters = {}
        self.Name = 'General description of script'
        self.Description = """ Does nothing """
        self.init_parameters()
        self.devList = ListOfDevices()
        self.inExecution = False
        self.inTermination = False
        #self.executionThread = 
        return
    def _run(self):
        """
        actual test script
        override this method with actual script
        """
        raise NotImplementedError
    def init_datastore(self,filename):
        self.datastore = OutputHandler(self.devList.list())
        self.datastore.setDataFileName(filename)
        self.dataFileName = filename
        return
    def terminate(self):
        self.inTermination = True
        return
    def get_datastore(self):
        """
        returns the datastore of the script
        """
        return  self.datastore
    def get_parameter_list(self):
        """
        returns a list of parameters with their properties 
        """
        list_of_parameters = []
        for key in self._parameters.keys():
            list_of_parameters.append(self._parameters[key])
        return list_of_parameters
    def set_parameter_value(self,Name, Value):
        response = self._parameters[Name].setValue(Value)
        return response
    def get_parameter_value(self, Name):
        Value = None
        if Name in self._parameters.keys():
            Value = self._parameters[Name].getValue()
        return Value
    def get_active_devices_list(self):
        return self.devList.list()
    def append_active_devices_list(self,device):
        device.setActive(True)
        self.devList.append(device)
    def get_data_header(self):
        datagramKeys = self.datastore.datagram.extract_header()
        return datagramKeys
    def generate_parameter(self, Name='NoParameter',Unit ='Arb.U.', Type=None, Iterable=None, Limits = [ None, None, None], Description='self explanatory'):
        """
        creates the object with parameter properties
        Name
        Unit
        Type
        Value
        Limits
        Description
        """
        parameter = GeneralParameter(Name,Unit, Type,Iterable, Limits, Description)
        # copy the parameter to a structure containing all parameters
        # under the same name
        self._parameters[Name] = parameter
        #print parameter.values['Name']
        return parameter
    def init_parameters(self):
        """
        inits the input parameters edited before starting the test
        override this method with actual script
        """
        raise NotImplementedError
    def init_devices(self):
        """
        inits the devices edited before starting the test
        override this method with actual script
        is should return the list of active devices
        """
        raise NotImplementedError
    def initExecution(self,filenamePath):
        """
        preparation for running the test
        """
        print('Init devices')
        self.init_devices()
        print('Init data file')
        self.init_datastore(filenamePath)
        (dirname,filename) = os.path.split(filenamePath)
        
        self.datastore.report( ('STARTING: %(script)s, dataFile: %(filename)s' % \
                            {'script':self.get_Name(), "filename":filename}) )
        return
    def Execute(self):
        
        self._run()
        (dirname,filename) = os.path.split(self.dataFileName)
        self.datastore.report( ('FINISHED: %(script)s, dataFile: %(filename)s' % \
                            {'script':self.get_Name(), "filename":filename}) )
        self.close_devices()
        return
    def observe(self,duration, delay=0.5):
        """general repeating data acquisition cycle"""
        self.timer.zeroTimer()
        while self.timer.getSinceLastZeroed() < duration:    # observe the temperature variables for about 5 min, wait for the Temp to stabilize
            self.timer.Wait(delay)
            for device in self.get_active_devices_list():
                device.Measure()
                # check if we are isntructed to terminate:
                if self.inTermination:
                    raise JobTerminationException
            self.datastore.acquireData()
    def close_devices(self):
        for device in self.get_active_devices_list():
                #self.datastore.report('closing device...%s' %str(device))
                device.Close()
    def get_Name(self):
        """
        just returns some descriptive string
        """
        return self.Name
    def get_Description(self):
        """
        just returns some descriptive string
        """
        return self.Description
    def generate_script_description_text(self):
        #collumn = event.GetColumn()
        scriptName = self.get_Name()
        scriptDescribe = self.get_Description()
        Parameters = self.get_parameter_list()
        #paramDescribe = ''
        paramDescRows = [[scriptName],[scriptDescribe]]
        paramDescRows.append(["Parameters:"])
        for param in Parameters:
            parName = param.getName()
            parValue = param.getValue()
            parUnit = param.getUnit()
            parDesc = param.getDescription()
            paramRow = [str(parName),str(parValue), str(parUnit), str(parDesc)]
            paramDescRows.append(paramRow)
            #paramDescribe = param.getName() + param
        return paramDescRows
   