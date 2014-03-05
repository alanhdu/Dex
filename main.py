import wx
import wx.lib.sheet
from Data import Data
from Stats import StatsMenu
from Graphs import GraphMenu
import warnings
warnings.simplefilter("error")

class MainWindow(wx.Frame):
    """ Master Window"""
    output, sheet = None, None
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

        bsizer = wx.BoxSizer(wx.VERTICAL)
        self.output = wx.TextCtrl(self, 
                style=wx.TE_MULTILINE | wx.TE_READONLY)
        # use monospace font
        f = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL)
        self.output.SetFont(f)
        self.sheet = wx.lib.sheet.CSheet(self)
        self.sheet.SetNumberRows(14)
        self.sheet.SetNumberCols(15)
        self.sheet.EnableEditing(False)
        bsizer.Add(self.output, 1, wx.EXPAND)
        bsizer.AddSpacer(30)
        bsizer.Add(self.sheet, 1, wx.EXPAND)

        self.SetSizer(bsizer)


    def onExit(self, e):
        self.Close(True)
    def onOpen(self, event):
        self.dirname = ""
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.csv", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.data = Data(dlg.GetPath(), self)
        dlg.Destroy()
        self.sheet.Clear()

        rows, cols = self.data.shape()
        self.sheet.SetNumberCols(cols)
        self.sheet.SetNumberRows(rows)

        for i, name in enumerate(self.data.names()):
            self.sheet.SetColLabelValue(i, name)
            for j, val in enumerate(self.data[name]):
                self.sheet.SetCellValue(j, i, str(val))

app = wx.App(False)
frame = MainWindow()
app.MainLoop()
