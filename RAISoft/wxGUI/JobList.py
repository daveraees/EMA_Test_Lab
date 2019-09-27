import threading
#import thread
import Queue
import wx
import traceback
import os
import csv
import sys
#import uuid

#from EMA_joblist_window_xrc import xrcFRA_JOBLIST
from GuiExceptions import JobTerminationException
# redirect the standard program output to the window in the console



class TextCtrlFileLike(wx.TextCtrl):
    """
    class for capturing the sys.stdout
    into wTextCtrl
    """
    def write(self,text): 
        self.Clear()
        self.AppendText(text)  
        return
class TextCtrlFileLikeAppend(wx.TextCtrl):
    """
    class for capturing the sys.stdout
    into wTextCtrl
    """
    def write(self,text): 
        self.AppendText(text)  
        return


class JobListFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        kwds["size"] = (500,600)  
        wx.Frame.__init__(self, *args, **kwds)
        self.Colours = wx.ColourDatabase()
        # setup the queue for script processing
        self.maxQueueMembers = 20 
        self.jobQueue = Queue.Queue(self.maxQueueMembers)
        # maintain the pool of added scripts
        self.scriptList = dict()
        
        self.LST_JOBS = wx.ListCtrl(parent=self, size=(500,100), style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.LST_JOBS.InsertColumn(0,"Test script")
        self.LST_JOBS.InsertColumn(1,"Data file")
        self.LST_JOBS.InsertColumn(2,"Status")
        self.LST_JOBS.InsertColumn(3,"Directory")
        self.CurrentTestPosition = 0    # store the actual position in the queue
        self.processQueue = True
        
        self.TXT_JOB_DESCRIPTION = TextCtrlFileLikeAppend(parent=self , size=(500,200),style=wx.TE_AUTO_SCROLL|wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_LEFT)
        self.TXT_JOB_DESCRIPTION.AppendText("<Description of the jobs>\n")
        self.writer = csv.writer(self.TXT_JOB_DESCRIPTION, delimiter='\t')
        
        self.TXT_STDOUT = TextCtrlFileLikeAppend(parent=self, size=(500,100), style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_LINEWRAP)
        sys.stdout = self.TXT_STDOUT
        
        self.TXT_STDOUT.AppendText("<Output of the program>\n")
        
        self.backgndTest = threading.Thread(target=self._runTest)
        self.backgndTest.setDaemon(True)
        #self.backgndTest.start()  
        
        self.PNL_BTNS = wx.Panel(parent=self,id=wx.NewId())
        self.BTN_UP = wx.Button(parent=self.PNL_BTNS,id=wx.ID_UP)
        self.BTN_UP.Enable(False)
        self.BTN_DOWN = wx.Button(parent=self.PNL_BTNS,id=wx.ID_DOWN)
        self.BTN_DOWN.Enable(False)
        self.BTN_DELETE = wx.Button(parent=self.PNL_BTNS,id=wx.ID_DELETE)
        self.BTN_STOP = wx.Button(parent=self.PNL_BTNS,id=wx.ID_STOP)
        self.BTN_RUN = wx.Button(parent=self.PNL_BTNS,id=-1,label = 'Run next')
        
        self.__set_properties()
        self.__do_layout()
        # couple the EVENTS
        self._create_bindings()
        return
    def _create_bindings(self):
        self.Bind(event=wx.EVT_LIST_ITEM_SELECTED, handler=self.OnSelectJob, source=self.LST_JOBS)
        self.Bind(event=wx.EVT_CLOSE,handler=self.OnClose)
        #self.Bind(wx.EVT_BUTTON, self.OnBtnDOWN, source=self.BTN_DOWN)
        #self.Bind(wx.EVT_BUTTON, self.OnBtnUP, source=self.BTN_UP)
        self.Bind(wx.EVT_BUTTON, self.OnBtnDELETE, source=self.BTN_DELETE)
        self.Bind(wx.EVT_BUTTON, self.OnBtnSTOP, source=self.BTN_STOP)
        self.Bind(wx.EVT_BUTTON, self.OnBtnRUN, source=self.BTN_RUN)
    def __set_properties(self):
        self.SetTitle("List of measurement jobs")
        return
    def __do_layout(self):
        # tool panel
        sizer_BTNS = wx.BoxSizer(wx.HORIZONTAL)
        sizer_BTNS.Add(self.BTN_UP,1,wx.ALL|wx.EXPAND, 5)
        sizer_BTNS.Add(self.BTN_DOWN,1, wx.ALL|wx.EXPAND, 5)
        sizer_BTNS.Add(self.BTN_DELETE,1, wx.ALL|wx.EXPAND, 5)
        sizer_BTNS.Add(wx.StaticLine(self.PNL_BTNS, style=wx.LI_VERTICAL), 0, wx.ALL|wx.EXPAND, 5)
        sizer_BTNS.Add(self.BTN_STOP,1,wx.ALL|wx.EXPAND, 5)
        sizer_BTNS.Add(self.BTN_RUN,1,wx.ALL|wx.EXPAND, 5)
        self.PNL_BTNS.SetSizer(sizer_BTNS)
        sizer_BTNS.Fit(self.PNL_BTNS)
        self.PNL_BTNS.Layout()
        
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.PNL_BTNS,0, wx.EXPAND)
        sizer_1.Add(self.LST_JOBS, 1, wx.EXPAND) 
        sizer_1.Add(self.TXT_JOB_DESCRIPTION, 2, wx.EXPAND) 
        sizer_1.Add(self.TXT_STDOUT, 1, wx.EXPAND) 
        self.SetSizer(sizer_1)
        
        sizer_1.Fit(self)
        self.Layout()
        return
    def _create_script_execution_thread(self):
        # script queue processing thread
        self.backgndTest = threading.Thread(target=self._runTest)
        self.backgndTest.setDaemon(True)
        self.backgndTest.start()  
        return
    def insertJob(self,testJob):
        """
        inserts a specified measurement task into the script FIFO queue and
        manages the queue display
        """
        (workDir,filename) = os.path.split(testJob['dataFileName'])
        jobName = testJob['script'].get_Name()
        #position = testJob["position"] = self.LST_JOBS.GetItemCount()
        JobIdentifier = wx.NewId()
        #position = testJob["identifier"] = JobIdentifier
        #insert the test script ready for execution into the list of jobs:
        self.LST_JOBS.Append([jobName,filename,'Waiting in queue...',workDir])
        # assign the unique identifier to the unique data, so I can find it later
        self.LST_JOBS.SetItemData(self.LST_JOBS.GetItemCount()-1,JobIdentifier)
        #self.LST_JOBS.SetStringItem(position ,1,filename)
        #self.LST_JOBS.SetStringItem(position,2,)
        #self.LST_JOBS.SetStringItem(position,3,workDir)
        #self.scriptList.append(script)
        self.scriptList[str(JobIdentifier)] = testJob
        #self.jobQueue.put(item=testJob, block=True, timeout=1)
        #self.backgndTest.
        self.start_processing()
        #self.Fit()
        return
    def stop_processing(self):
        self.processQueue = False
        return
    def start_processing(self):
        self.processQueue = True
        if not self.backgndTest.isAlive():
            self._create_script_execution_thread()
        return
    def get_processing(self):
        return self.processQueue
    def _runTest(self):
        while self.CurrentTestPosition < self.LST_JOBS.GetItemCount():
            if not self.get_processing():
                break
            #testJob = self.jobQueue.get(block=True)  # obtain the script to run
            JobIdentifier = self.LST_JOBS.GetItemData(self.CurrentTestPosition)
            # pick a waiting job from the pool
            testJob = self.scriptList[str(JobIdentifier)]
            #script = testJob['script']
            #script.graphic = testJob['PlotWindow']
            testJob['PlotWindow'].Show()
            testJob['PlotWindow'].Raise()
            filenamePath = testJob['dataFileName']
            #(workDir,filename) = os.path.split(filenamePath)
            #position = testJob["position"] # position in the list
            # prepare the script for execution
            self.UpdateJobEntry(self.CurrentTestPosition,'LIGHT BLUE','Preparing devices...')
            previous_action_OK = True
            try:
                testJob['script'].initExecution(filenamePath)
            except:
                self.UpdateJobEntry(self.CurrentTestPosition,'RED','Error occurred during initialization of the devices')
                previous_action_OK = False
                print traceback.print_exc(file=self.TXT_JOB_DESCRIPTION)
                #self.TXT_JOB_DESCRIPTION.write(str(sys.exc_info()[0]))
                #self.TXT_JOB_DESCRIPTION.write(str(sys.exc_info()[1]))
                #self.TXT_JOB_DESCRIPTION.write(str(sys.exc_info()[2]))
                testJob['script'].close_devices()
                #raise
            
            if previous_action_OK:
                testJob['PlotWindow'].bind_data(testJob['script'].get_datastore())
            if previous_action_OK:
                try:
                    self.UpdateJobEntry(self.CurrentTestPosition,'PINK','Executing test...')
            
                    testJob['PlotWindow'].start_acquizition()
                    returnValue = testJob['script'].Execute()
                except JobTerminationException:
                    self.UpdateJobEntry(self.CurrentTestPosition,'ORANGE','User terminated the test')
                    print "User terminated the test"
                    previous_action_OK = False
                    self.stop_processing()
                    testJob['script'].close_devices()
                except:
                    self.UpdateJobEntry(self.CurrentTestPosition,'RED','Error occurred during test execution')
                    print "Unexpected error:" 
                    print traceback.print_exc()
                    #self.TXT_JOB_DESCRIPTION.write(str(sys.exc_info()[0]))
                    #self.TXT_JOB_DESCRIPTION.write(str(sys.exc_info()[1]))
                    #self.TXT_JOB_DESCRIPTION.write(str(sys.exc_info()[2]))
                    previous_action_OK = False
                    testJob['script'].close_devices()
            if previous_action_OK:
                self.UpdateJobEntry(self.CurrentTestPosition,'GREEN','Test finished without error')
                #stoop the acquizition graphics
            testJob['PlotWindow'].acquizitionRunning = False
            self.CurrentTestPosition = self.CurrentTestPosition + 1
            if not self.get_processing():
                break
        if self.get_processing():
            self.stop_processing()
        return
    def UpdateJobEntry(self,LineNumber,colour,text):
        self.LST_JOBS.SetStringItem(LineNumber,2,text)
        self.LST_JOBS.SetItemBackgroundColour(LineNumber,self.Colours.FindName(colour) )
        return
    def extract_job_item(self,JobListIndex):
        #NumCols = self.LST_JOBS.GetColumnCount()
        testIdentificator = self.LST_JOBS.GetItemData(JobListIndex)
        testJob = self.scriptList[str(testIdentificator)]
        (workDir,filename) = os.path.split(testJob['dataFileName'])
        jobName = testJob['script'].get_Name()
        testDescription = [jobName,filename,'Waiting in queue...',workDir]
        print testIdentificator, filename
        jobItem = (testDescription,testIdentificator)
        return jobItem
    def OnSelectJob(self,event):
        scriptListIdx = event.GetIndex()
        identifier = self.LST_JOBS.GetItemData(scriptListIdx)
        paramDescRows = self.scriptList[str(identifier)]['script'].generate_script_description_text()
        self.writer.writerows(paramDescRows)
        #self.writer.writerows(self.extract_job_item(scriptListIdx))
        self.scriptList[str(identifier)]['PlotWindow'].Show()
        self.scriptList[str(identifier)]['PlotWindow'].Raise()
        return 
    def OnBtnDELETE(self,event):
        itemIdx = self.LST_JOBS.GetFirstSelected()
        if itemIdx > self.CurrentTestPosition:
            identificator = self.LST_JOBS.GetItemData(itemIdx)
            unwantedTest = self.scriptList.pop(str(identificator))
            unwantedTest['PlotWindow'].Destroy()
            self.LST_JOBS.DeleteItem(itemIdx)
            
        return
    def OnBtnUP(self,event):
        itemIdx = self.LST_JOBS.GetFirstSelected()
        NumCols = self.LST_JOBS.GetColumnCount()
        if itemIdx > self.CurrentTestPosition+1:
            for col in range(NumCols):
                SelectedJob = self.LST_JOBS.GetItem(itemIdx)
                AboveJob = self.LST_JOBS.GetItem(itemIdx-1)
                SelectedJob.SetId(itemIdx-1)
                AboveJob.SetId(itemIdx)
            self.LST_JOBS.Select(itemIdx-1, on=1)
        return
    
#    def OnBtnUP(self,event):
#        testJobList = []
#        #itemDataList = []
#        #self.writer.writerows(['Button UP clicked','no actio'])
#        itemIdx = self.LST_JOBS.GetFirstSelected()
#        if itemIdx > self.CurrentTestPosition+1:
#            #ExtractedItem = self.LST_JOBS.GetItem(itemIdx)
#            # remove the selected item from the Listctrl and add it to the beginning of temporary list
#            testJobList.append(self.extract_job_item(itemIdx))
#            self.LST_JOBS.DeleteItem(itemIdx)
#            # remove all the following items from the LIST CTRL and store them in the temporary list
#            for idx in range(itemIdx-1, self.LST_JOBS.GetItemCount()):
#                testJobList.append(self.extract_job_item(idx))
#                self.LST_JOBS.DeleteItem(idx)
#            # self.LST_JOBS.InsertItem(itemIdx-1,ExtractedItem)
#            for testJobItem in testJobList:
#                (testDescription, identificator) = testJobItem
#                self.LST_JOBS.Append(testDescription)
#                self.LST_JOBS.SetItemData(self.LST_JOBS.GetItemCount()-1,identificator)
#            # select previouslyu selected item:
#            self.LST_JOBS.Select(itemIdx-1, on=1)
#        else:
#            pass
#        return
    def OnBtnDOWN(self,event):
        self.writer.writerows(['Button DOWN clicked','No action'])
        itemIdx = self.LST_JOBS.GetFocusedItem()
        self.writer.writerows(self.LST_JOBS.GetItemText(itemIdx))
        return
    def OnBtnSTOP(self,event):
        if self.get_processing():
            itemIdx = self.CurrentTestPosition
            identificator = self.LST_JOBS.GetItemData(itemIdx)
            unwantedTest = self.scriptList.pop(str(identificator))
            unwantedTest['script'].terminate()
        return
    def OnBtnRUN(self,event):
        self.start_processing()
        return
    def OnClose(self,event):
        self.Show(False)
        return
    