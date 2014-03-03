import wx
from Data import Data
from matplotlib import pyplot as plt
from Dialogues import ColumnSelect
from scipy import stats
import numpy as np

class GraphMenu(wx.Menu):
    def __init__(self, parent):
        wx.Menu.__init__(self)
        self.parent = parent
        hist = self.Append(wx.NewId(), 'Histogram', "Histogram")
        parent.Bind(wx.EVT_MENU, self.createHist, hist)

        boxplot = self.Append(wx.NewId(), 'Boxplot', "Boxplot")
        parent.Bind(wx.EVT_MENU, self.createBoxplot, boxplot)

    def createHist(self, event):
        dlg = wx.Dialog(self.parent, title="Histogram input")
        cs = ColumnSelect(dlg, self.parent.data, ("Select Data",))
        hsize = wx.BoxSizer(wx.HORIZONTAL)

        histOptions = wx.Panel(dlg)
        vsize1 = wx.BoxSizer(wx.VERTICAL)

        hsize1 = wx.BoxSizer(wx.HORIZONTAL)
        bars = wx.CheckBox(histOptions, label="Bars")
        density = wx.CheckBox(histOptions, label="Density")
        bars.SetValue(True)
        hsize1.Add(bars)
        hsize1.Add(density)
        vsize1.Add(hsize1)

        # TODO avoid hardcoding sizes. Play with fonts to get width
        hsize2 = wx.BoxSizer(wx.HORIZONTAL)
        hsize2.Add(wx.StaticText(histOptions, label="# of Bins"))
        numBins = wx.SpinCtrl(histOptions, min=1, max=999, size=(50, -1))
        numBins.SetValue(np.sqrt(self.parent.data.shape()[1]))
        hsize2.Add(numBins)
        vsize1.Add(hsize2)

        hsize3 = wx.BoxSizer(wx.HORIZONTAL)
        hsize3.Add(wx.StaticText(histOptions, label="Density Bandwidth"))
        bandwidth = wx.SpinCtrl(histOptions, value="0", min=-10, max=10, size=(50, -1))
        bandwidth.SetRange(-10, 10)
        hsize3.Add(bandwidth)
        vsize1.Add(hsize3)

        histOptions.SetSizer(vsize1)

        hsize.Add(histOptions)
        hsize.AddSpacer(20)
        hsize.Add(cs, flag=wx.EXPAND)

        vsize = wx.BoxSizer(wx.VERTICAL)
        vsize.Add(hsize, 1, flag=wx.EXPAND) #don't know why the 1 is necessary

        
        ok = wx.Button(dlg, -1, "OK")
        ok.Bind(wx.EVT_BUTTON, lambda x: dlg.Close())
        vsize.Add(ok)


        dlg.SetSizer(vsize)
        dlg.ShowModal()
        ds = cs.GetValue()
        dlg.Destroy()

        # TODO legend

        a = min(np.nanmin(self.parent.data[d]) for d in ds)
        b = max(np.nanmax(self.parent.data[d]) for d in ds)
        x = np.arange(a, b, (b-a) / 1000.0)
        bins = np.arange(a, b, float(b-a) / 10.0)

        for d in ds:
            data = self.parent.data[d]
            data = data[np.isfinite(data)]
            if bars.GetValue():
                plt.hist(data, bins=bins, alpha=0.7/len(ds), normed=density.GetValue())
            if density.GetValue():
                dens = stats.kde.gaussian_kde(data)
                plt.plot(x, dens(x), color="b")

        plt.show()

    def createBoxplot(self, event):
        dlg = wx.Dialog(self.parent, title="Boxplot Input")
        cs = ColumnSelect(dlg, self.parent.data, ("Select Data",))
        vsize = wx.BoxSizer(wx.VERTICAL)
        vsize.Add(cs, 1, wx.EXPAND)

        ok = wx.Button(dlg, -1, "OK")
        ok.Bind(wx.EVT_BUTTON, lambda x: dlg.Close())
        vsize.Add(ok)

        dlg.SetSizer(vsize)

        dlg.ShowModal()
        ds = cs.GetValue()
        dlg.Destroy()

        for d in ds:
            data = self.parent.data[d]
            data = data[np.isfinite(data)]
            plt.boxplot(data)
        plt.show()
