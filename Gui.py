import wx
from Data import Data
from Stats import StatsMenu
from Graphs import GraphMenu

class MainWindow(wx.Frame):
    """ Master Window"""
    def __init__(self, size=(600, 600)):
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

        statMenu = StatsMenu()
        menubar.Append(statMenu, "&Stats")

        graphMenu = GraphMenu(self)
        menubar.Append(graphMenu, "&Graphs")
        self.Show(True)

        bsizer = wx.BoxSizer()
        self.control = wx.TextCtrl(self, 
                style=wx.TE_MULTILINE | wx.TE_READONLY)
        bsizer.Add(self.control, 1, wx.EXPAND)
        bsizer.SetMinSize(size)

        self.SetSizerAndFit(bsizer)


    def onExit(self, e):
        self.Close(True)
    def onOpen(self, event):
        self.dirname = ""
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.csv", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.data = Data(dlg.GetPath(), self)
        dlg.Destroy()
        self.control.Clear()
        self.control.WriteText("\n".join(x for x in self.data.names()))


app = wx.App(False)
frame = MainWindow()
app.MainLoop()
