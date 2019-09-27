import wx
class ParentModalDialog(wx.Frame):
    def __init__(self, parent, title="My Dialog"):
        wx.Frame.__init__(self, parent, -1, title=title, size=(200,100), style=wx.FRAME_FLOAT_ON_PARENT | wx.CAPTION | wx.FRAME_TOOL_WINDOW)
        panel = wx.Panel(self, -1)

        self.callback = None
        self.cancelCallback = None

        mainsizer = wx.BoxSizer(wx.VERTICAL)

        ctrlsizer = wx.BoxSizer(wx.HORIZONTAL)
        ctrlsizer.Add(wx.StaticText(panel, -1, "Foo:"), wx.ALL, 5)
        self.textctrl = wx.TextCtrl(panel, -1)
        ctrlsizer.Add(self.textctrl, 0, wx.ALL, 5)

        mainsizer.Add(ctrlsizer, 1, wx.EXPAND)

        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        okbutton = wx.Button(panel, wx.ID_OK, "OK")
        cancelbutton = wx.Button(panel, wx.ID_CANCEL, "Cancel")
        buttonsizer.Add(okbutton, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsizer.Add(cancelbutton, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        mainsizer.Add(buttonsizer)

        panel.SetSizer(mainsizer)
        panel.Layout()
        mainsizer.Fit(self)
        okbutton.SetDefault()
        okbutton.Bind(wx.EVT_BUTTON, self.OnOK)
        cancelbutton.Bind(wx.EVT_BUTTON, self.OnCancel)

    def Show(self, callback=None, cancelCallback=None):
        self.callback = callback
        self.cancelCallback = cancelCallback

        self.CenterOnParent()
        self.GetParent().Enable(False)
        wx.Frame.Show(self)
        self.Raise()
    def OnOK(self, event):
        try:
            if self.callback:
                self.callback(self.textctrl.GetValue())
        finally:
            self.GetParent().Enable(True)

        self.Destroy()

    def OnCancel(self, event):
        try:
            if self.cancelCallback:
                self.cancelCallback()
        finally:
            self.GetParent().Enable(True)

        self.Destroy()
class TestFrame(wx.Frame):
    def __init__(self, parent, **kwargs):
        wx.Frame.__init__(self, parent, -1, size=(400,300), **kwargs)
        panel = wx.Panel(self, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.textctrl = wx.TextCtrl(panel, -1)
        choice = wx.Choice(panel, -1, choices=['Choice-1', 'Choice-2', 'Choice-3'], size=(200,20))

        sizer.Add(self.textctrl, 0, wx.EXPAND)
        sizer.Add(choice)
        btn = wx.Button(panel, -1, "Block Me")
        sizer.Add(btn)

        panel.SetSizer(sizer)
        panel.Layout()

        btn.Bind(wx.EVT_BUTTON, self.OnBlock)

    def OnBlock(self, event):
        dlg = ParentModalDialog(self)
        dlg.Show(callback=self._ReceiveAnswer, cancelCallback=self._ReceiveCancellation)

    def _ReceiveAnswer(self, value):
        self.textctrl.SetValue(value)

    def _ReceiveCancellation(self):
        print "Dialog was cancelled! Oh well!"
class TestApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        frame1 = TestFrame(None, title="Testing Frame #1", pos=(20,20))
        frame2 = TestFrame(None, title="Testing Frame #2", pos=(200,200))
        frame1.Show(True)
        frame2.Show(True)

        self.SetTopWindow(frame1)
        return True
def main(*args, **kwargs):
    app = TestApp(0)
    app.MainLoop()
if __name__ == "__main__":
    main()
