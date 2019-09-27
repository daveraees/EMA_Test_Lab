""" This is application for the control of the CELIV experiment
It runs in interactive mode for signal optimalization, then 
when you are happy with teh signal, it can be downloaded from the osciloscope
""" 

# test run setup

# Major libraries imports:
import wx
import copy
import sys
import wx.xrc as xrc
import wx.aui

import matplotlib as mpl
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as Canvas

# Project GUI libraries imports
from ControlFrameCELIV_xrc import xrcBANANA
from RAISoft.wxGUI.parameterEdit import editParCtrl
from RAISoft.Output.Output_for_gui import OutputHandler

#from RAISoft.wxGUI.JobList import JobListFrame
from RAISoft.wxGUI.GraphMPL import Plot

from CELIVexperiment import Test


#ID_SHOWJOBS = wx.NewId()


class CELIVcontrolDialog(xrcBANANA):
    def __init__(self, parent, **kwargs):
        # bind the script to control:
        self.script = Test()
        
        xrcBANANA.__init__(self, parent, **kwargs)
        #self.PNL_PARAM_EDIT = NamedPanel(self,'Edit the script parameters below')
        #self.PNL_PARAM_EDIT.setup()
        
        #self.SriptsBase = ScriptsBase
        self.dataFilenamePath = None
        self.dataFilename = None
        self.dataDirectory = None
        # the controlling 
        self.paramList = []
        self.dataFilenameSet = False
        self.scriptSelected = True
#        self.load_sripts_tree()
        # create attributes for the named items in this container
        #self.MEN_BAR = self.GetMenuBar() 
        #self.BTN_OUTPUT = self.getControl("BTN_OUTPUT")
        #self.BTN_RUN = self.getControl("BTN_RUN")
        
        # create place for the tprobe signal plot
        self.figure = mpl.figure.Figure(dpi=None, figsize=(2,2))
        self.canvas = Canvas(self, -1, self.figure)
        self.axes = self.figure.gca()
        self.axes.set_title('Probe pulse shape',visible=True)
        self.axes.set_xlabel('Time, t (s)',visible=True)
        self.axes.set_ylabel('Voltage, U (V)',visible=True)
        mainVSizer = self.GetSizer()
        #mainVSizer = wx.Sizer()
        mainVSizer.Insert(2,self.canvas,0 , wx.GROW | wx.EXPAND)
        self.Layout()
        # important fields
        self.MEN_BAR = self.GetMenuBar()
        self.TXT_FILENAME = self.getControl("TXT_FILENAME")
        self.TXT_DIRECTORY = self.getControl("TXT_DIRECTORY")
        self.PNL_PARAM_EDIT = self.getControl("PNL_PARAM_EDIT")
        self.TXT_DESRIPTION = self.getControl("TXT_DESCRIPTION")
        self.SCOPE_POINTS = self.getControl("SCOPE_POINTS")
        
        #buttons
        self.BTN_SINGLE = self.getControl("BTN_SINGLE")
        self.BTN_REPEAT = self.getControl("BTN_REPEAT")
        self.BTN_RECORD = self.getControl("BTN_RECORD")
        self.BTN_OUTPUT = self.getControl("BTN_OUTPUT")
        
#        showMenu = wx.Menu()
#        showMenu.Append(ID_SHOWJOBS, 'Show list of test jobs')#, kind=wx.ITEM_CHECK)
#        #showMenu.Append(ID_SHOWGRAPH, 'Show graph')#, kind=wx.ITEM_CHECK)
#        self.MEN_BAR.Append(showMenu,'Show')
#        # show additional frames
#        self.joblist = JobListFrame(self)
#        self.joblist.Show()
#        #self.graph = Plot(self)
        
        
        self._create_bindings()
        self.load_parameters()
        return
    def getControl(self, xmlid):
        '''Retrieves the given control (within a dialog) by its xmlid'''
        control = self.FindWindowById(xrc.XRCID(xmlid))
        if control == None and self.GetMenuBar() != None:  # see if on the menubar
          control = self.GetMenuBar().FindItemById(xrc.XRCID(xmlid))
        assert control != None, 'Programming error: a control with xml id ' + xmlid + ' was not found.'
        return control
    def _create_bindings(self):
        #wx.EVT_LEFT_DOWN 
        #wx.EVT_
        # script list events
        # Button events
        self.Bind(wx.EVT_BUTTON, self.OnOutputBtn, source=self.BTN_RECORD)
        self.Bind(wx.EVT_TEXT, self.OnTextChange, source=self.TXT_DESRIPTION)
        return
    def _createParamCtrl(self, parameter):
        """ 
        create a control for each parameter 
        """
        editParCtrl(self,parameter)
        return
    def load_parameters(self):
        #self.PNL_PARAM_EDIT.dynamicControlList = []
        #self.parametersList.init_parameters()
        self.PNL_PARAM_EDIT.DestroyChildren()
        self.script.init_interactive_parameters()
        self.paramList = self.script.get_parameter_list()
        #print paramList
        self.paramVSizer =  wx.FlexGridSizer(rows=0, cols=2, vgap=0, hgap=0) 
        self.PNL_PARAM_EDIT.SetSizer(self.paramVSizer) 
        self.PNL_PARAM_EDIT.SetAutoLayout(True)
        for par in self.paramList:
            self._createParamCtrl(par)
            for collumn in range( self.paramVSizer.GetCols() ):
                self.paramVSizer.Add(wx.StaticLine(self.PNL_PARAM_EDIT,), 0, wx.ALL|wx.EXPAND, 5)
            
            self.paramVSizer.Fit(self.PNL_PARAM_EDIT)
            self.paramVSizer.SetSizeHints(self.PNL_PARAM_EDIT)
        
        #self.paramVSizer
        self.PNL_PARAM_EDIT.SetSizer(self.paramVSizer)
        self.PNL_PARAM_EDIT.SetAutoLayout(True)
        self.paramVSizer.Fit(self.PNL_PARAM_EDIT)
        self.paramVSizer.SetSizeHints(self.PNL_PARAM_EDIT)
        
        # readjust the window to fit all the loaded parameters
        self.Fit()
        #self.PNL_PARAM_EDIT.setup()
        return
    def _update_description_box(self,text):
        #self.TXT_DESRIPTION.Clear()
        self.TXT_DESRIPTION.AppendText('\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n')
        self.TXT_DESRIPTION.AppendText(text)
        return
    def _run_script(self,dataFileName):
        self._unset_readiness()
        # create the copy of script that was set up for running
        testJob = {}
        testJob['script'] = copy.deepcopy(self.script)
        testJob['dataFileName'] = copy.deepcopy(dataFileName)
        graphic = Plot(self)
        graphic.set_my_title(dataFileName)
        graphic.Show(True)
        testJob['PlotWindow'] = graphic
        self.joblist.insertJob(testJob)
        return
    def OnOutputBtn(self,event):
        """
        open the choose file dialog
        """
        
        
        
        
        # select the waveform data filename
        # Args below are: parent, question, dialog title, default answer
        dd = wx.FileDialog( parent=self, 
                            message="Select file to save measured data", 
                            defaultDir="~/", 
                            defaultFile='', 
                            wildcard='*.dat',
                            style=wx.wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)

        # This function returns the button pressed to close the dialog
        ret = dd.ShowModal()

        # Let's check if user clicked OK or pressed ENTER
        if ret == wx.ID_OK:
            self.dataFilenamePath = dd.GetPath()
            # create an empty file for the save data to prevent overwriting
            datafileKeeper = open(self.dataFilenamePath, 'w')
            datafileKeeper.close()
            self.dataDirectory = dd.GetDirectory()
            self.dataFilename = dd.GetFilename()
            self.TXT_FILENAME.Clear()
            self.TXT_FILENAME.write(self.dataFilename)
            self.TXT_DIRECTORY.Clear()
            self.TXT_DIRECTORY.write(self.dataDirectory)
            self.dataFilenameSet = True
        else:
            pass
        
        
        #create the data structure
        datastore = OutputHandler(self.devList.list())
        datastore.setDataFileName(self.dataFilenamePath)
        
        # download the data from the instrument
        waveform = self.script.record_scope()
        #copy the data to the datastore 
        datastore.acquireData()
        # display measured data on graphic
        PulseFigure = Plot()
        PulseFigure.bind_data(datastore)
        PulseFigure.start_acquizition()
        # stop the re-plotting thread
        PulseFigure.acquizitionRunning = False
        PulseFigure.set_my_title(self.dataFilenamePath)
        PulseFigure.Show(True)
        
        return
    def OnTextChange(self,event):
        """
        called when the text in description box has changed
        and updates the plot parameters
        """
        # find the values of test parameters
        FinalVoltage = self.script.get_parameter_value('Final Voltage')
        StaticVoltage = self.script.get_parameter_value('Static Voltage')
        StaticTime = self.script.get_parameter_value('Static Time')
        ScanSpeed = self.script.get_parameter_value('Scan Speed')
        PulseNumber = self.script.get_parameter_value('Pulse Number')
        
        #calculate the x and y:
        VsweepMag = (StaticVoltage - FinalVoltage)
        VsweepTime = abs (VsweepMag / ScanSpeed)
        
        index = []
        values = []
        TotalTime = 0.0
        index.append(TotalTime)
        values.append(StaticVoltage)
        for i in range(PulseNumber):
            TotalTime = TotalTime + StaticTime
            index.append(TotalTime)
            values.append(StaticVoltage)
            TotalTime = TotalTime + VsweepTime
            index.append(TotalTime)
            values.append(FinalVoltage)
            index.append(TotalTime)
            values.append(StaticVoltage)
            pass
        
        #index = [0.0, StaticTime, StaticTime+VsweepTime, StaticTime+VsweepTime]
        #values = [StaticVoltage, StaticVoltage, FinalVoltage, StaticVoltage]
        
        # recreate the plot
        self.axes.clear()
        self.axes.plot(index, values, c='r', lw=3.0)
        self.axes.autoscale_view()
        self.canvas.draw()
        return
