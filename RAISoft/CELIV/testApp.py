import wx
import sys
#sourcePATH = r"D:\workspace\EMA2\src"
sourcePATH = r"c:\Documents and Settings\Rais\workspace\EMA2\src"

sys.path.insert(0,sourcePATH)

from celiv_control import CELIVcontrolDialog


class MyApp(wx.App):
    def OnInit(self):
        self.frame = CELIVcontrolDialog(None)
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return True

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
