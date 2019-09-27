#!/usr/bin/env python
# -*- coding: utf-8 -*-
# generated by wxGlade 0.5 on Thu Dec 27 18:02:20 2007
# project libraries imports:
# instruments:
from RAISoft.gui_scripts.GenericScript import TestScript

#import wx
    
class Test(TestScript):
    def __init__(self):
        
        TestScript.__init__(self)
        self.Name = 'CELIV'
        self.Description = """
    The script for measurement of Charge-Extraction by Linearly Increasing Voltage
    """
        return
    def init_parameters(self):
        """
        describe the the parameters for non-interactive experiment control 
        and initialize some basic values
        """
#        self.generate_parameter(Name='Scope',
#                                Unit='name', 
#                                Type='name', 
#                                Iterable = False, 
#                                Limits = [ None, None, ['Agilent Scope','HP Scope']], 
#                                Description='Device to record the time evolution of the current pulse')
#        self.set_parameter_value('Scope', 'Agilent Scope')
#        
#        self.generate_parameter(Name='Probe',
#                                Unit='name', 
#                                Type='name', 
#                                Iterable = False, 
#                                Limits = [ None, None, ['Agilent Generator','HP Generator']], 
#                                Description='Device to apply the PROBE Voltage pulse')
#        self.set_parameter_value('Probe', 'Agilent Generator')
        
        self.generate_parameter(Name='Light Pulse',
                                Unit='name', 
                                Type='name', 
                                Iterable = False, 
                                Limits = [ None, None, ['None','Laser']], 
                                Description='Device to apply the PROBE Ligth pulse')
        self.set_parameter_value('Light Pulse', 'None')
        #self.init_interactive_parameters()
        return
    def init_interactive_parameters(self):
        """
        describe the the parameters for interactive experiment control 
        and initialize some basic values
        """
        # no predefined parameters
        self.generate_parameter(Name='Static Time',
                                Unit='seconds', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ None, 2e-8, None], 
                                Description='Set time to hold static value of voltage before ramping')
        self.set_parameter_value('Static Time', 1.0)
        
        self.generate_parameter(Name='Static Voltage',
                                Unit='Volts', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ +5.0, -5.0, None], 
                                Description='Set voltage to hold before ramping')
        self.set_parameter_value('Static Voltage', 0.0)
        
        self.generate_parameter(Name='Scan Speed',
                                Unit='Volts per seconds', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ None, 1e-3, None], 
                                Description='Set speed of voltage change during scan ramping')
        self.set_parameter_value('Scan Speed', 1.0)
        
        self.generate_parameter(Name='Final Voltage',
                                Unit='Volts', 
                                Type='float', 
                                Iterable = False, 
                                Limits = [ +5.0, -5.0, None], 
                                Description='Set final voltage to reach during ramping')
        self.set_parameter_value('Final Voltage', 0.0)
        
        self.generate_parameter(Name='Pulse Number',
                                Unit='', 
                                Type='count', 
                                Iterable = False, 
                                Limits = [ 10, 1, None], 
                                Description='Set final voltage to reach during ramping')
        self.set_parameter_value('Pulse Number', 1)
        
        return
    
    def init_devices(self):
#        self.scope_device_name = self.get_parameter_value('Scope')
#        self.probe_device_name = self.get_parameter_value('Probe')
        self.pulse_device_name = self.get_parameter_value('Light Pulse')
        
        from DummyDevices import Clock
        self.Stopwatch = Clock()
        self.append_active_devices_list(self.Stopwatch)
        
        
        #from Devices import Scope,Sawtooth
        #self.Scope = Scope()
        #self.append_active_devices_list(self.Scope)
        #self.Sawtooth = Sawtooth()
        #self.append_active_devices_list(self.Sawtooth)
        self.init_interactive_parameters()
        return
    def _run(self):
        """ 
        CELIV experiment control is interactive
        this only downloads the data
        """
        
        
        
        return
    def set_scope_timescale(self):
        print 'configuring timescale'
        return
    def set_generated_pulse(self):
        print 'uploading pulse'
        return
    def record_scope(self):
        print 'downloading osciloscope patch'
        return
    def trigger(self):
        'sending trigger signal'
        return
    


#from AllScripts import ScriptsBase
#ScriptsBase.add_script(Test, 'Obscure')