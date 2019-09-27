import wx
import copy
import sys
import wx.xrc as xrc
#import sys
#modulePATH=r'd:\David\programm\EMA'
#sys.path.insert(0,modulePATH)
#from NamedPanel import NamedPanel

ID_ABOUT = wx.NewId()
ID_EXIT  = wx.NewId()
ID_SHOWGRAPH = wx.NewId()
ID_SHOWJOBS = wx.NewId()
ID_MAINWINDOW = wx.NewId()

from EMA_startup_window_xrc import xrcHEAD
from RAISoft.gui_scripts.AllScripts import ScriptsBase
from parameterEdit import editParCtrl

from GraphMPL import Plot
from JobList import JobListFrame

#sys.path.insert()

class HeadWindow(xrcHEAD):
    def __init__(self,*args,**kwargs):
        xrcHEAD.__init__(self,*args,**kwargs)
        #self.PNL_PARAM_EDIT = NamedPanel(self,'Edit the script parameters below')
        #self.PNL_PARAM_EDIT.setup()
        self.SriptsBase = ScriptsBase
        self.dataFilenamePath = None
        self.dataFilename = None
        self.dataDirectory = None
        # the controlling 
        self.paramList = []
        self.dataFilenameSet = False
        self.scriptSelected = False
#        self.load_sripts_tree()
        # create attributes for the named items in this container
        self.MEN_BAR = self.GetMenuBar() 
        self.BTN_OUTPUT = self.getControl("BTN_OUTPUT")
        self.BTN_RUN = self.getControl("BTN_RUN")
        self.TXT_FILENAME = self.getControl("TXT_FILENAME")
        self.TXT_DIRECTORY = self.getControl("TXT_DIRECTORY")
        self.LST_CATEGORIES = self.getControl("LST_CATEGORIES")
        self.LST_SCRIPTS = self.getControl("LST_SCRIPTS")
        self.PNL_PARAM_EDIT = self.getControl("PNL_PARAM_EDIT")
        self.TXT_DESRIPTION = self.getControl("TXT_DESRIPTION")
        
        self.load_script_categories()
        self.load_scripts('All')
#        self.graph = PlotFrame(parent=self)
#        self.graph.Show()
        #self._createParamCtrl()
        
        # create menu
        showMenu = wx.Menu()
        showMenu.Append(ID_SHOWJOBS, 'Show list of test jobs')#, kind=wx.ITEM_CHECK)
        #showMenu.Append(ID_SHOWGRAPH, 'Show graph')#, kind=wx.ITEM_CHECK)
        self.MEN_BAR.Append(showMenu,'Show')
        # show additional frames
        self.joblist = JobListFrame(self)
        self.joblist.Show()
        #self.graph = Plot(self)
        
        self._create_bindings()
        return
    def getControl(self, xmlid):
        '''Retrieves the given control (within a dialog) by its xmlid'''
        control = self.FindWindowById(xrc.XRCID(xmlid))
        if control == None and self.GetMenuBar() != None:  # see if on the menubar
          control = self.GetMenuBar().FindItemById(xrc.XRCID(xmlid))
        assert control != None, 'Programming error: a control with xml id ' + xmlid + ' was not found.'
        return control

    def _check_readiness(self):
        if self.dataFilenameSet:
            self._update_description_box("Data file name selected?...OK")
        else:
            self._update_description_box("Select NEW data file NAME")
        ready = self.dataFilenameSet * self.scriptSelected
        if self.scriptSelected:
            self._update_description_box("Script selected?...OK")
        else:
            self._update_description_box("Select script for testing")
        # test if the parameters are not None
        for par in self.paramList:
            if not par.getValue() == None:
                parReady = True
            else:
                parReady = False
            self._update_description_box(( par.getName()+ ' parameter UPDATED?  '+ str(bool(parReady)) ))
            ready = ready * parReady
        return ready
    def _unset_readiness(self):
        self.dataFilenameSet = False
        #self.scriptSelected = False
        return
    def _create_bindings(self):
        #wx.EVT_LEFT_DOWN 
        #wx.EVT_
        # script list events
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnClickedScriptCategory, source=self.LST_CATEGORIES)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnClickedScript, source=self.LST_SCRIPTS)
        # Button events
        self.Bind(wx.EVT_BUTTON, self.OnOutputBtn, source=self.BTN_OUTPUT)
        self.Bind(wx.EVT_BUTTON, self.OnRunBtn, source=self.BTN_RUN)
        #self.Bind(wx.EVT_MENU,self.OnGraphWiewMenu,id=ID_SHOWGRAPH)
        self.Bind(wx.EVT_MENU,self.OnJobsWiewMenu,id=ID_SHOWJOBS)
        
        
        return
    def _createParamCtrl(self, parameter):
        """ 
        create a control for each parameter 
        """
        editParCtrl(self,parameter)
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
    def _update_description_box(self,text):
        #self.TXT_DESRIPTION.Clear()
        self.TXT_DESRIPTION.AppendText('\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n')
        self.TXT_DESRIPTION.AppendText(text)
        return
    def load_parameters(self,category,scriptName):
        #self.PNL_PARAM_EDIT.dynamicControlList = []
        #self.parametersList.init_parameters()
        self.PNL_PARAM_EDIT.DestroyChildren()
        self.script = self.SriptsBase.find_script(category, scriptName)
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
    def load_script_categories(self):
        """
        build the test script categories listing
        """
        _scriptCatList = self.SriptsBase.get_script_categories()
        for catName in _scriptCatList: 
            self.LST_CATEGORIES.Append([catName])
        idxAll = self.LST_CATEGORIES.FindItem(0, self.SriptsBase.category_all_name, partial=True)
        self.LST_CATEGORIES.Select(idxAll,True)
        return
    def load_scripts(self,category):
        """
        build list of script names in given category
        """
        self.LST_SCRIPTS.DeleteAllItems()
        _scriptNameList = self.SriptsBase.get_scripts_in_category(category)
        for scriptName in _scriptNameList: 
            self.LST_SCRIPTS.Append([scriptName])
        return
    def load_description(self,category,scriptname):
        description = self.SriptsBase.get_script_description(category, scriptname)
        self._update_description_box(description)
        return 
    def OnClickedScript(self, event):
        """
        display the description to the clicked script
        """
        _script_Name = event.GetText()
        categoryItem = self.LST_CATEGORIES.GetFirstSelected()
        category = self.LST_CATEGORIES.GetItemText(categoryItem)
        description = self.load_description(category, _script_Name)
        self.load_parameters(category, _script_Name)
        self.scriptSelected = True
        #self.LST_SCRIPTS
        return
    def OnClickedScriptCategory(self, event):
        """
        display the description to the clicked script
        """
        _category_Name = event.GetText()
        #category = ''
        scritpList = self.load_scripts(_category_Name)
        return
    def OnOutputBtn(self,event):
        """
        open the choose file dialog
        """
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

        # The dialog is not in the screen anymore, but it's still in memory
        #for you to access it's values. remove it from there.
        dd.Destroy()
        return True
    def OnRunBtn(self,event):
        ready = self._check_readiness()
        if ready:
            self.BTN_RUN.Enable(True) 
        if ready:
            self._run_script(self.dataFilenamePath)
        return
#    def OnGraphWiewMenu(self,event):
#        checked = event.IsChecked ()
#        self.graph.Show(True)
#        return
    def OnJobsWiewMenu(self,event):
        checked = event.IsChecked ()
        self.joblist.Show(True)
        self.joblist.Raise()
        return
    
class MyApp(wx.App):
    def OnInit(self):
        frame = HeadWindow(None,id=ID_MAINWINDOW)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
