import wx
from matplotlib import pyplot as plt
import seaborn as sns


class SettingsMenu(wx.Menu):
    def __init__(self, parent):
        wx.Menu.__init__(self)
        self.parent = parent

        parent.Bind(wx.EVT_MENU, self.toggleShell,
                self.Append(wx.NewId(), 'Toggle Shell'))
        parent.Bind(wx.EVT_MENU, self.toggleScript,
                self.Append(wx.NewId(), 'Toggle Scripter'))
    def toggleShell(self, event):
        pass
    def toggleScript(self, event):
        pass
