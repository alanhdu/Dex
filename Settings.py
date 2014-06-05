import wx
from matplotlib import pyplot as plt
import seaborn as sns
from Dialogues import GraphSettings

settings = {}

class SettingsMenu(wx.Menu):
    funcs, settings = None, None
    def __init__(self, parent):
        wx.Menu.__init__(self)
        self.funcs = {}
        self.parent = parent

        parent.Bind(wx.EVT_MENU, self.toggleShell,
                self.Append(wx.NewId(), 'Toggle Shell'))
        parent.Bind(wx.EVT_MENU, self.toggleScript,
                self.Append(wx.NewId(), 'Toggle Scripter'))
        self.AppendSeparator()
        parent.Bind(wx.EVT_MENU, self.graphSettings,
                self.Append(wx.NewId(), 'Graph Settings'))
        
        """ Default Settings """
        settings["style"] = "whitegrid"
        self.funcs["style"] = sns.set_style

        settings["color"] = "bright"
        self.funcs["color"] = sns.set_palette

        settings["cmap"] = "coolwarm"

        settings["Title Size"] = 36
        self.funcs["Title Size"] = self.changeTitle
        settings["Legend Size"] = 22
        self.funcs["Legend Size"] = self.changeLegend
        settings["Axis Size"] = 28
        self.funcs["Axis Size"] = self.changeAxis
        settings["Tick Size"] = 16
        self.funcs["Tick Size"] = self.changeTick

        for k, f in self.funcs.iteritems():
            f(settings[k])

    def changeTitle(self, x):
        plt.rcParams["axes.titlesize"] = x
    def changeLegend(self, x):
        plt.rcParams["legend.fontsize"] = x
    def changeAxis(self, x):
        plt.rcParams["axes.labelsize"] = x
    def changeTick(self, x):
        plt.rcParams["xtick.labelsize"] = x
        plt.rcParams["ytick.labelsize"] = x
    def toggleShell(self, event):
        pass
    def toggleScript(self, event):
        pass
    def graphSettings(self, event):
        dlg = GraphSettings(self.parent, settings)
        if dlg.ShowModal() == wx.ID_OK:
            d = dlg.GetValue()
            for key in d:
                if d[key] != settings[key]:
                    settings[key] = d[key]
                    if key in self.funcs:
                        self.funcs[key](d[key])
                        print key
