import wx
import sys


from RAISoft.wxGUI.MainWindow import HeadWindow

class MyApp(wx.App):
    def OnInit(self):
        self.frame = HeadWindow(None)
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return True

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
