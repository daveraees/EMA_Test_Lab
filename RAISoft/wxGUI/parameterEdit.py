# contains set of controls for script parameter editing

import wx
import numpy

from wx.lib.agw.floatspin import FloatSpin, EVT_FLOATSPIN
from wx.lib.agw.rulerctrl import RulerCtrl


class singleFloat:
    def __init__(self,parent, parameter):
        self.parent = parent
        self.HorizontalOneParam = wx.BoxSizer(wx.HORIZONTAL) 
        self.parameter = parameter
        paramName = self.parameter.getName()
        paramType = self.parameter.getType()
        paramUnit = self.parameter.getUnit()
        self.parNameLabel = wx.Button(parent.PNL_PARAM_EDIT, label=(paramName +'\n in ' + paramUnit))
        
        self.parValueCtrl = FloatSpin(parent.PNL_PARAM_EDIT)
        # setup the limits and value for the float control
        [upperLimit, lowerLimit, allowedList] = self.parameter.getLimits()
        self.parValueCtrl.SetRange(lowerLimit,upperLimit)
        self.parValueCtrl.SetFormat(fmt='%e')
        self.parValueCtrl.SetDigits(digits=3)
        paramValue = self.parameter.getValue()        
        if not paramValue == None:
            self.parValueCtrl.SetValue(paramValue)
        try:
            increment =  (upperLimit - lowerLimit)/10.0
        except:
             increment = 1 
        self.parValueCtrl.SetIncrement(increment)
        
        # setup the limits and value for the float control if there is list of allowed values
        if not allowedList == None:
            self.parValueCtrl.Destroy()
            self.parValueCtrl = wx.Choice(parent.PNL_PARAM_EDIT)
            for value in allowedList:
                item = ('%8.3e' % value)
                self.parValueCtrl.Append(item)
            paramValue = self.parameter.getValue()
            paramValueItem = ('%8.3e' % paramValue)
            #print paramValueItem
            if not paramValue == None:
                idXDefault = self.parValueCtrl.FindString(paramValueItem)
                self.parValueCtrl.Select(idXDefault)
            else:
                self.parValueCtrl.Select(0)
        #self.parTypeLabel = wx.StaticText(parent.PNL_PARAM_EDIT, label=paramType[0])
        #self.HorizontalOneParam.Add(self.parNameLabel, 0, wx.ALL, 5)
        self.HorizontalOneParam.Add(wx.StaticLine(parent.PNL_PARAM_EDIT, style=wx.LI_VERTICAL), 0, wx.ALL|wx.EXPAND, 5)
        self.HorizontalOneParam.Add(self.parValueCtrl, 1, wx.ALL|wx.EXPAND, 5)
        #self.HorizontalOneParam.Add(self.parTypeLabel,0, wx.ALL, 5)
        
        parent.paramVSizer.Add(self.parNameLabel, 0, wx.ALIGN_LEFT)
        parent.paramVSizer.Add(self.HorizontalOneParam, 0, wx.ALIGN_LEFT)
        
        
        
        # binding events
        parent.Bind(wx.EVT_BUTTON, self.OnDescribeBTN, source=self.parNameLabel)
        # decire if it is an choice or it is FloatSpin
        try:
            self.parValueCtrl.GetSelection()
            parent.Bind(wx.EVT_CHOICE, self.OnEditParam, source=self.parValueCtrl)
        except:
            self.parValueCtrl.Bind(EVT_FLOATSPIN, self.OnEditParam, source=self.parValueCtrl)
        return
    def OnEditParam(self,event):
        """
        Update the given parameter according to control
        """
        floatValue = 'No value found'
        try:
            value = event.GetString()
            floatValue = float(value)
        except:
            floatValue = self.parValueCtrl.GetValue()
            pass
        #print floatValue
        self.parameter.setValue(floatValue)
        acutalValue =  self.parameter.getValue()
        try:
            self.parValueCtrl.SetValue(acutalValue)
        except:
            pass
        self.parent._update_description_box(( 'Parameter "%(name)s"  updated to %(value)s (%(unit)s)' % \
                                         {'name':self.parameter.getName(), 'value':str(acutalValue), 'unit':self.parameter.getUnit() }))
        return
    def OnDescribeBTN(self,event):
        """
        Gives hint about the parameter
        """
        parDescribe = self.parameter.getDescription()
        self.parent._update_description_box(parDescribe)

class singleInt:
    def __init__(self,parent, parameter):
        self.parent = parent
        self.HorizontalOneParam = wx.BoxSizer(wx.HORIZONTAL) 
        self.parameter = parameter
        paramName = self.parameter.getName()
        paramType = self.parameter.getType()
        paramUnit = self.parameter.getUnit()
        self.parNameLabel = wx.Button(parent.PNL_PARAM_EDIT, label=(paramName +'\n in ' + paramUnit))
        
        self.parValueCtrl = wx.SpinCtrl(parent.PNL_PARAM_EDIT)
        # setup the limits and value for the float control
        [upperLimit, lowerLimit, allowedList] = self.parameter.getLimits()
        if upperLimit == None:
            upperLimit = 0
        if lowerLimit == None:
            lowerLimit = 999
        self.parValueCtrl.SetRange(lowerLimit,upperLimit)
        paramValue = self.parameter.getValue()        
        if not paramValue == None:
            self.parValueCtrl.SetValue(paramValue)
        
        # setup the limits and value for the float control if there is list of allowed values
        if not allowedList == None:
            self.parValueCtrl.Destroy()
            self.parValueCtrl = wx.Choice(parent.PNL_PARAM_EDIT)
            for value in allowedList:
                item = (str(value))
                self.parValueCtrl.Append(item)
            paramValue = self.parameter.getValue()
            paramValueItem = (str(paramValue))
            #print paramValueItem
            if not paramValue == None:
                idXDefault = self.parValueCtrl.FindString(paramValueItem)
                self.parValueCtrl.Select(idXDefault)
            else:
                self.parValueCtrl.Select(0)
        #self.parTypeLabel = wx.StaticText(parent.PNL_PARAM_EDIT, label=paramType[0])
        #self.HorizontalOneParam.Add(self.parNameLabel, 0, wx.ALL, 5)
        self.HorizontalOneParam.Add(wx.StaticLine(parent.PNL_PARAM_EDIT, style=wx.LI_VERTICAL), 0, wx.ALL|wx.EXPAND, 5)
        self.HorizontalOneParam.Add(self.parValueCtrl, 1, wx.ALL|wx.EXPAND, 5)
        #self.HorizontalOneParam.Add(self.parTypeLabel,0, wx.ALL, 5)
        
        parent.paramVSizer.Add(self.parNameLabel, 0, wx.ALIGN_LEFT)
        parent.paramVSizer.Add(self.HorizontalOneParam, 0, wx.ALIGN_LEFT)
        
        
        
        # binding events
        parent.Bind(wx.EVT_BUTTON, self.OnDescribeBTN, source=self.parNameLabel)
        # decire if it is an choice or it is FloatSpin
        try:
            self.parValueCtrl.GetSelection()
            parent.Bind(wx.EVT_CHOICE, self.OnEditParam, source=self.parValueCtrl)
        except:
            self.parValueCtrl.Bind(wx.EVT_SPINCTRL, self.OnEditParam, source=self.parValueCtrl)
        return
    def OnEditParam(self,event):
        """
        Update the given parameter according to control
        """
        intValue = 'No value found'
        try:
            value = event.GetString()
            intValue = int(value)
        except:
            intValue = self.parValueCtrl.GetValue()
            pass
        #print floatValue
        self.parameter.setValue(intValue)
        acutalValue =  self.parameter.getValue()
        try:
            self.parValueCtrl.SetValue(acutalValue)
        except:
            pass
        self.parent._update_description_box(( 'Parameter "%(name)s"  updated to %(value)s (%(unit)s)' % \
                                         {'name':self.parameter.getName(), 'value':str(acutalValue), 'unit':self.parameter.getUnit() }))
        return
    def OnDescribeBTN(self,event):
        """
        Gives hint about the parameter
        """
        parDescribe = self.parameter.getDescription()
        self.parent._update_description_box(parDescribe)


class arrayFloat:
    def __init__(self,parent, parameter):
        self.parent = parent
        # obtain the paramter to edit
        self.parameter = parameter
        paramName = self.parameter.getName()
        paramType = self.parameter.getType()
        paramUnit = self.parameter.getUnit()
        
        # construct the parameter controls
        self.parNameLabel = wx.Button(parent.PNL_PARAM_EDIT, label=(paramName +'\n in ' + paramUnit))
        self.parValueCtrlFromLabel = wx.StaticText(parent.PNL_PARAM_EDIT, label="From:")
        self.parValueCtrlFrom =  FloatSpin(parent.PNL_PARAM_EDIT)
        self.parValueCtrlToLabel = wx.StaticText(parent.PNL_PARAM_EDIT, label="To:")
        self.parValueCtrlTo =  FloatSpin(parent.PNL_PARAM_EDIT)
        self.parValueCtrlPointsLabel = wx.StaticText(parent.PNL_PARAM_EDIT, label="Points:")
        self.parValueCtrlPoints = wx.SpinCtrl(parent.PNL_PARAM_EDIT)
        self.parValueCtrlPoints.SetRange(int(2),int(9999))
        self.parValueCtrlScale = wx.Choice(parent.PNL_PARAM_EDIT)
        self.parValueCtrlScale.AppendItems(['linear scale','log10 scale','arbitrary array'])
        self.parValueCtrlScale.Select(0)
        self.parValueCtrlResetArray = wx.Button(parent.PNL_PARAM_EDIT, label="Reset")
        self.parValueCtrlAppendArray = wx.Button(parent.PNL_PARAM_EDIT, label="Append")
        #self.parTypeLabel = wx.StaticText(parent.PNL_PARAM_EDIT, label=paramType[0])
        
        # get parameter limits
        # setup the limits and value for the float control
        [upperLimit, lowerLimit, allowedList] = self.parameter.getLimits()
        self.paramValue = self.parameter.getValue()
        if self.paramValue == None:
            self.paramValue = numpy.array([]) # creates an empty array
        # setup the bounds for the controls
        for control in [self.parValueCtrlFrom,self.parValueCtrlTo]:
            control.SetRange(lowerLimit,upperLimit)
            control.SetFormat(fmt='%e')
            control.SetDigits(digits=4)    
            try:
                increment =  (upperLimit - lowerLimit)/10.0
                control.SetIncrement(increment)
            except:
                 increment = 1 
            

        # cerate sizers
        self.HorizontalOneParam = wx.BoxSizer(wx.HORIZONTAL) 
        self.HorizontalUpper = wx.BoxSizer(wx.HORIZONTAL)
        self.HorizontalLower = wx.BoxSizer(wx.HORIZONTAL)
        self.VerticalParam = wx.BoxSizer(wx.VERTICAL)
        self.VerticalButtons = wx.BoxSizer(wx.VERTICAL)
        
        # fill upper H sizer
        self.HorizontalUpper.Add(self.parValueCtrlFromLabel, 0, wx.ALL, 5)
        self.HorizontalUpper.Add(self.parValueCtrlFrom, 1, wx.ALL|wx.EXPAND, 5)
        self.HorizontalUpper.Add(self.parValueCtrlToLabel, 0, wx.ALL, 5)
        self.HorizontalUpper.Add(self.parValueCtrlTo, 1, wx.ALL|wx.EXPAND, 5)
        
        # fill lower H sizzer
        self.HorizontalLower.Add(self.parValueCtrlPointsLabel, 0, wx.ALL, 5)
        self.HorizontalLower.Add(self.parValueCtrlPoints, 0, wx.ALL, 5)
        self.HorizontalLower.Add(self.parValueCtrlScale, 0, wx.ALL, 5)
        
        self.VerticalButtons.Add(self.parValueCtrlResetArray, 0, wx.ALL, 5)
        self.VerticalButtons.Add(self.parValueCtrlAppendArray, 0, wx.ALL, 5)
        
        # add Lower and upper sizer to single sizer
        self.VerticalParam.Add(self.HorizontalUpper, 0, wx.LEFT)
        self.VerticalParam.Add(self.HorizontalLower, 0, wx.LEFT)
        
        # add a parameter name, controls and typename
        #self.HorizontalOneParam.Add(self.parNameLabel, 0, wx.ALL, 5)
        self.HorizontalOneParam.Add(wx.StaticLine(parent.PNL_PARAM_EDIT, style=wx.LI_VERTICAL), 0, wx.ALL|wx.EXPAND, 5)
        self.HorizontalOneParam.Add(self.VerticalParam, 0, wx.LEFT)
        self.HorizontalOneParam.Add(wx.StaticLine(parent.PNL_PARAM_EDIT, style=wx.LI_VERTICAL), 0, wx.ALL|wx.EXPAND, 5)
        self.HorizontalOneParam.Add(self.VerticalButtons, 0, wx.LEFT)
        # add the controls to global parameters sizer
        parent.paramVSizer.Add(self.parNameLabel, 0, wx.ALIGN_LEFT)
        parent.paramVSizer.Add(self.HorizontalOneParam, 0, wx.ALIGN_LEFT)
        
        # bind the actions to the Create button
        parent.Bind(wx.EVT_BUTTON, self.OnDescribeBTN, source=self.parNameLabel)
        parent.Bind(wx.EVT_BUTTON, self.OnResetArrayBtn, source=self.parValueCtrlResetArray)
        parent.Bind(wx.EVT_BUTTON, self.OnAppendArrayBtn, source=self.parValueCtrlAppendArray)
        return
    def _get_array(self):
        paramFrom = self.parValueCtrlFrom.GetValue()
        paramTo = self.parValueCtrlTo.GetValue()
        paramPoints = self.parValueCtrlPoints.GetValue()
        scale = self.parValueCtrlScale.GetSelection()
        
        testArray = None # if nothing gets createds
        if scale == 0: # linear scale demanded
            testArray = numpy.linspace(paramFrom,paramTo,paramPoints)
        
        if scale == 1: # log scale demanded
            if (paramFrom * paramTo) > 0: # both parameters either positive or negative
                signFrom = paramFrom / abs(paramFrom)
                testArray = numpy.logspace(numpy.log10(paramFrom),numpy.log10(paramTo),paramPoints)
            else:
                testArray = None 
        if scale == 2: # arbitrary array edit
            testArray = None
        return testArray
    def OnResetArrayBtn(self,event):
        """
        Construct a new array from the parameters
        """
        #[paramFrom, paramTo, paramPoints, scale] = self._get_boundaries()
        testArray = self._get_array()
        if testArray == None:
            self.parent._update_description_box( "Wrong array creation values")
        else: # append the array to the already
            self.paramValue = testArray
        # update the parameter object:
        answer = self.parameter.setValue(self.paramValue)
        if answer:
            self.parent._update_description_box( answer)
        
        self.parent._update_description_box(( 'Parameter "%(name)s"  updated to the following array (in %(unit)s)\n%(value)s' % \
                                         {'name':self.parameter.getName(), 'value':str(self.parameter.getValue()), 'unit':self.parameter.getUnit() }))
        return
    def OnAppendArrayBtn(self,event):
        """
        Construct a new array from the parameters and append it to the end of previously created
        """
        testArray = self._get_array()
        if testArray == None:
            self.parent._update_description_box("Array not appended, wrong parameters")
        else: # append the array to the already
            self.paramValue = numpy.hstack([self.paramValue,testArray])
        answer = self.parameter.setValue(self.paramValue)
        if answer:
            self.parent._update_description_box( answer)
        self.parent._update_description_box(( 'Parameter "%(name)s"  updated to the following array (in %(unit)s)\n%(value)s' % \
                                         {'name':self.parameter.getName(), 'value':str(self.parameter.getValue()), 'unit':self.parameter.getUnit() }))
        return
    def OnDescribeBTN(self,event):
        """
        Gives hint about the parameter
        """
        parDescribe = self.parameter.getDescription()
        self.parent._update_description_box(parDescribe)
        return
    

class singleName:
    def __init__(self,parent, parameter):
        self.parent = parent
        self.HorizontalOneParam = wx.BoxSizer(wx.HORIZONTAL) 
        self.parameter = parameter
        paramName = self.parameter.getName()
        paramType = self.parameter.getType()
        paramUnit = self.parameter.getUnit()
        self.parNameLabel = wx.Button(parent.PNL_PARAM_EDIT, label=(paramName +'\n in ' + paramUnit))
        
        self.parValueCtrl = wx.TextCtrl(parent.PNL_PARAM_EDIT)
        # setup the limits and value for the float control
        [upperLimit, lowerLimit, allowedList] = self.parameter.getLimits()
        paramValue = self.parameter.getValue()        
        if not paramValue == None:
            self.parValueCtrl.SetValue(paramValue)
        
        # setup the limits and value for the float control if there is list of allowed values
        if not allowedList == None:
            self.parValueCtrl.Destroy()
            self.parValueCtrl = wx.Choice(parent.PNL_PARAM_EDIT)
            for value in allowedList:
                item = value
                self.parValueCtrl.Append(item)
            paramValue = self.parameter.getValue()
            paramValueItem = paramValue
            #print paramValueItem
            if not paramValue == None:
                idXDefault = self.parValueCtrl.FindString(paramValueItem)
                self.parValueCtrl.Select(idXDefault)
            else:
                self.parValueCtrl.Select(0)
        #self.parTypeLabel = wx.StaticText(parent.PNL_PARAM_EDIT, label=paramType[0])
        #self.HorizontalOneParam.Add(self.parNameLabel, 0, wx.ALL, 5)
        self.HorizontalOneParam.Add(wx.StaticLine(parent.PNL_PARAM_EDIT, style=wx.LI_VERTICAL), 0, wx.ALL|wx.EXPAND, 5)
        self.HorizontalOneParam.Add(self.parValueCtrl, 1, wx.ALL|wx.EXPAND, 5)
        #self.HorizontalOneParam.Add(self.parTypeLabel,0, wx.ALL, 5)
        
        parent.paramVSizer.Add(self.parNameLabel, 0, wx.ALIGN_LEFT)
        parent.paramVSizer.Add(self.HorizontalOneParam, 0, wx.ALIGN_LEFT)
        
        
        
        # binding events
        parent.Bind(wx.EVT_BUTTON, self.OnDescribeBTN, source=self.parNameLabel)
        # decire if it is an choice or it is FloatSpin
        try:
            self.parValueCtrl.GetSelection()
            parent.Bind(wx.EVT_CHOICE, self.OnEditParam, source=self.parValueCtrl)
        except:
            self.parValueCtrl.Bind(wx.EVT_TEXT_ENTER, self.OnEditParam, source=self.parValueCtrl)
        return
    def OnEditParam(self,event):
        """
        Update the given parameter according to control
        """
        intValue = 'No value found'
        try:
            value = event.GetString()
            intValue = value
        except:
            intValue = self.parValueCtrl.GetValue()
            pass 
        strValue = str(intValue)
        self.parameter.setValue(strValue)
        acutalValue =  self.parameter.getValue()
        print type(acutalValue), type(intValue) 
        try:
            self.parValueCtrl.SetValue(acutalValue)
        except:
            pass
        self.parent._update_description_box(( 'Parameter "%(name)s"  updated to %(value)s (%(unit)s)' % \
                                         {'name':self.parameter.getName(), 'value':str(acutalValue), 'unit':self.parameter.getUnit() }))
        return
    def OnDescribeBTN(self,event):
        """
        Gives hint about the parameter
        """
        parDescribe = self.parameter.getDescription()
        self.parent._update_description_box(parDescribe)

class editParCtrl:
    def __init__(self,parent,parameter):
        # attach the parameter to be controlled and the output field
        parType = parameter.getType()
        if parType[0]=='float':
            if parType[1]: # iterable
                self.parameterEdit = arrayFloat(parent,parameter)
            else:
                self.parameterEdit = singleFloat(parent,parameter)
        if parType[0]=='count':
            self.parameterEdit = singleInt(parent,parameter)
        if parType[0]=='name':
            self.parameterEdit = singleName(parent,parameter)
        else:
            pass
        #self.descriptionBox = descriptionBox
        return
    def OnSelectParameter(self,event):
        print 'value edited'
        event.GetText
        self.parameter.setValue()
        return
