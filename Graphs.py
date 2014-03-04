import wx
from Data import Data
from matplotlib import pyplot as plt
from Dialogues import ColumnSelect, GraphDialog
from scipy import stats
import numpy as np
import seaborn as sns

sns.set(style="whitegrid")

class GraphMenu(wx.Menu):
    def __init__(self, parent):
        wx.Menu.__init__(self)
        self.parent = parent
        hist = self.Append(wx.NewId(), 'Histogram')
        parent.Bind(wx.EVT_MENU, self.createHist, hist)

        boxplot = self.Append(wx.NewId(), 'Boxplot')
        parent.Bind(wx.EVT_MENU, self.createBoxplot, boxplot)

        violin = self.Append(wx.NewId(), "Violinplot")
        parent.Bind(wx.EVT_MENU, self.createViolin, violin)

        self.AppendSeparator()

        time = self.Append(wx.NewId(), "Time Series")
        parent.Bind(wx.EVT_MENU, self.createTime, time)

        scatter = self.Append(wx.NewId(), "Scatter Plot")
        parent.Bind(wx.EVT_MENU, self.createScatter, scatter)


    def createHist(self, event):
        # TODO avoid hardcoding sizes. Find smart way to decide on sizes 
        dlg = wx.Dialog(self.parent, title="Histogram input", size=(500, 200))
        cs = ColumnSelect(dlg, self.parent.data, ("Select Data",))
        hsize = wx.BoxSizer(wx.HORIZONTAL)

        # options
        vsize1 = wx.BoxSizer(wx.VERTICAL)

        hsize1 = wx.BoxSizer(wx.HORIZONTAL)
        bars = wx.CheckBox(dlg, label="Bars")
        density = wx.CheckBox(dlg, label="Density")
        bars.SetValue(True)
        hsize1.Add(bars)
        hsize1.Add(density)
        vsize1.Add(hsize1)

        hsize2 = wx.BoxSizer(wx.HORIZONTAL)
        hsize2.Add(wx.StaticText(dlg, label="# of Bins"))
        numBins = wx.SpinCtrl(dlg, min=1, max=999, 
                initial=np.sqrt(len(self.parent.data)), size=(50, -1))
        # default numBins = sqrt(Num of data points)
        hsize2.Add(numBins)
        vsize1.Add(hsize2)

        hsize3 = wx.BoxSizer(wx.HORIZONTAL)
        hsize3.Add(wx.StaticText(dlg, label="Density Bandwidth"))
        bandwidth = wx.SpinCtrl(dlg, value="0", min=-99, max=99, size=(50, -1))
        hsize3.Add(bandwidth)
        vsize1.Add(hsize3)

        hsize.Add(vsize1)
        hsize.AddSpacer(20)
        hsize.Add(cs, flag=wx.EXPAND)

        vsize = wx.BoxSizer(wx.VERTICAL)
        vsize.Add(hsize, 1, flag=wx.EXPAND) #don't know why the 1 is necessary

        ok = wx.Button(dlg, -1, "OK")
        ok.Bind(wx.EVT_BUTTON, lambda x: dlg.Close())
        vsize.Add(ok)

        dlg.SetSizer(vsize)
        dlg.ShowModal()
        ds = list(zip(*cs.GetValue())[0])
        dlg.Destroy()

        a = np.nanmin(self.parent.data[ds])
        b = np.nanmax(self.parent.data[ds])
        x = np.arange(a, b, (b-a) / 1000.0)
        bins = np.arange(a, b, float(b-a) / numBins.GetValue())

        bars, density = bars.GetValue(), density.GetValue() 
        bandwidth = np.exp(-0.2 * bandwidth.GetValue())

        for d in ds:
            data = self.parent.data[d].astype(float)
            # astype float b/c of bug in seaborn. 

            if bars and not density:
                plt.hist(data, bins=bins, alpha=1.0/len(ds), label=d)
            else:
                data = data[np.isfinite(data)]
                bw = stats.gaussian_kde(data).factor * bandwidth
                if density and not bars:
                    sns.kdeplot(data, shade=True, label=d, bw=bw)
                else:
                    sns.distplot(data, bins=bins, kde_kws={"bw":bw, "label":d})
        plt.legend(loc='best')
        plt.show()

    def createBoxplot(self, event):
        dlg = GraphDialog(self.parent, "Boxplot Input", queries=("Select Data",),
                size=(500, 200))
        dlg.ShowModal()
        ds = list(zip(*dlg.GetValue())[0])
        dlg.Destroy()

        sns.boxplot(self.parent.data[ds])
        plt.show()

    def createViolin(self, event):
        dlg = GraphDialog(self.parent, "Violinplot Input", ("Select Data",),
                size=(500, 200))
        dlg.ShowModal()
        ds = list(zip(*dlg.GetValue())[0])
        dlg.Destroy()

        # TODO Allow user input for bandwidth
        sns.violinplot(self.parent.data[ds])
        plt.show()

    def createTime(self, event):
        dlg = GraphDialog(self.parent, "Time Series Input", ("Select Data",), 
                size=(500, 200))

        dlg.ShowModal()
        ds = list(zip(*dlg.GetValue())[0])
        dlg.Destroy()

        self.parent.data[ds].plot()
        plt.show()

    def createScatter(self, event):
        dlg = wx.Dialog(self.parent, title="Scatterplot Input", size=(700, 200))
        cs = ColumnSelect(dlg, self.parent.data, ("X","Y"))
        vsize = wx.BoxSizer(wx.VERTICAL)

        hsize = wx.BoxSizer(wx.HORIZONTAL)
        vsize1 = wx.BoxSizer(wx.VERTICAL)
        regress = wx.CheckBox(dlg, label="Add Regression Lines?")
        vsize1.Add(regress)

        hsize.Add(vsize1)
        hsize.AddSpacer(20)
        hsize.Add(cs, 1, wx.EXPAND)

        vsize.Add(hsize, 1, wx.EXPAND)

        ok = wx.Button(dlg, -1, "OK")
        ok.Bind(wx.EVT_BUTTON, lambda x: dlg.Close())
        vsize.Add(ok)

        dlg.SetSizer(vsize)

        dlg.ShowModal()
        ds = cs.GetValue()
        dlg.Destroy()
        regress = regress.GetValue()
        data = self.parent.data[[x for xs in ds for x in xs]].astype(float)

        for x, y in ds:
            print x, y
            sns.lmplot(x, y, data)
        plt.show()

