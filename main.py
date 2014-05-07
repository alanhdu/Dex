import wx
import wx.lib.sheet
import wx.py
from Data import Data, Data1
from Stats import StatsMenu
from Graphs import GraphMenu
import sys
import traceback
from matplotlib import pyplot as plt

class MainWindow(wx.Frame):
    """ Master Window"""
    output, sheet, shell = None, None, None
    def __init__(self, size=(1000, 900)):
        wx.Frame.__init__(self, None, title="OpenStat", size=size)

        menubar = wx.MenuBar()
        self.SetMenuBar(menubar)

        filemenu = wx.Menu()
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open", "Open a csv file")
        filemenu.Append(wx.ID_ABOUT, "&About", "Info about OpenStat")
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", "Terminate OpenStat")
        menubar.Append(filemenu, "&File")

        self.Bind(wx.EVT_MENU, self.onExit, menuExit)
        self.Bind(wx.EVT_MENU, self.onOpen, menuOpen)

        edit = wx.Menu()
        menubar.Append(edit, "&Edit")

        statMenu = StatsMenu(self)
        menubar.Append(statMenu, "&Stats")

        graphMenu = GraphMenu(self)
        menubar.Append(graphMenu, "&Graphs")
        self.Show(True)

        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.output = wx.TextCtrl(self, 
                style=wx.TE_MULTILINE | wx.TE_READONLY)
        # use monospace font
        f = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL)
        self.output.SetFont(f)
        self.output.AppendText("Open a csv to begin\n")

        # spreadsheet
        self.sheet = Data1(self)
        self.data = self.sheet
        """
        self.sheet = wx.lib.sheet.CSheet(self)
        self.sheet.SetNumberRows(14)
        self.sheet.SetNumberCols(15)
        self.sheet.EnableEditing(False)
        """
        vsizer.Add(self.output, 1, wx.EXPAND)
        vsizer.AddSpacer(15)
        vsizer.Add(self.sheet, 1, wx.EXPAND)

        self.SetSizer(vsizer)

        self.Maximize()

    def onExit(self, e):
        self.Close(True)
    def onOpen(self, event):
        self.dirname = ""
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.csv", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.data.readFile(dlg.GetPath())
        dlg.Destroy()
    def onError(self, t, value, trace):
        message = "\n".join(traceback.format_exception(t, value, trace))
        dlg = wx.MessageDialog(self, message, "Error!", wx.OK|wx.ICON_ERROR)
        plt.clf() # clear figure
        dlg.ShowModal()

if __name__ == "__main__":
    app = wx.App(False)
    frame = MainWindow()
    sys.excepthook = frame.onError
    app.MainLoop()
