import wx
from Data import Data
from matplotlib import pyplot as plt
from Dialogues import ColumnSelect

class GraphMenu(wx.Menu):
    def __init__(self, parent):
        wx.Menu.__init__(self)
        self.parent = parent
        hist = self.Append(wx.NewId(), 'Histogram', "Histogram")
        parent.Bind(wx.EVT_MENU, self.createHist, hist)

    def createHist(self, event):
        dlg= ColumnSelect(self.parent, wx.NewId(), "Histogram input", 
                ("Select Data",))
        dlg.ShowModal()
        d = dlg.GetValue()
        dlg.Destroy()

        data = self.parent.data[d[0]]

        plt.hist(data)
        plt.show()
