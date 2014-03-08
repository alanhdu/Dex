import wx
from matplotlib import pyplot as plt
from Dialogues import GraphDialog
from scipy import stats
import numpy as np
import seaborn as sns
import pandas as pd
import warnings

warnings.simplefilter("error", np.RankWarning)

sns.set(style="whitegrid")

class GraphMenu(wx.Menu):
    def __init__(self, parent):
        wx.Menu.__init__(self)
        self.parent = parent

        # 1 Dimension
        parent.Bind(wx.EVT_MENU, self.createHist,
                self.Append(wx.NewId(), 'Histogram'))
        parent.Bind(wx.EVT_MENU, self.createBoxplot,
                self.Append(wx.NewId(), 'Boxplot'))
        parent.Bind(wx.EVT_MENU, self.createViolin,
                self.Append(wx.NewId(), "Violinplot"))
        parent.Bind(wx.EVT_MENU, self.createQQ,
                self.Append(wx.NewId(), "QQ Plot"))
        self.AppendSeparator()

        # Regression
        parent.Bind(wx.EVT_MENU, self.createTime,
                self.Append(wx.NewId(), "Time Series"))
        parent.Bind(wx.EVT_MENU, self.createScatter,
                self.Append(wx.NewId(), "Scatter Plot"))
        parent.Bind(wx.EVT_MENU, self.createMatrix, 
                self.Append(wx.NewId(), "Matrix Plot"))
        parent.Bind(wx.EVT_MENU, self.createInteraction, 
                self.Append(wx.NewId(), "Interaction Plot"))

        # Multivariate
        self.AppendSeparator()
        parent.Bind(wx.EVT_MENU, self.createBiDensity, 
                self.Append(wx.NewId(), "Bivariate Density Fit"))


    def createHist(self, event):
        # TODO avoid hardcoding sizes. Find smart way to decide on sizes 
        dlg = GraphDialog(self.parent, "Histogram Input", ("Select Data",),
                size=(500,200))

        # options
        hsize1 = wx.BoxSizer(wx.HORIZONTAL)
        bars = wx.CheckBox(dlg, label="Bars")
        density = wx.CheckBox(dlg, label="Density")
        bars.SetValue(True)
        density.SetValue(True)
        hsize1.Add(bars)
        hsize1.Add(density)
        dlg.Add(hsize1)

        numBins = dlg.AddSpinCtrl("# of Bins", 1, 999, 
                np.sqrt(len(self.parent.data)), size=(50, -1))
        bandwidth = dlg.AddSpinCtrl("Density Bandwidth", -99, 99, 0,
                size=(50, -1))

        bars.Bind(wx.EVT_CHECKBOX, lambda e: numBins.Enable(bars.GetValue()))
        density.Bind(wx.EVT_CHECKBOX, 
                lambda e: bandwidth.Enable(density.GetValue()))

        if dlg.ShowModal() == wx.ID_OK:
            ds = list(zip(*dlg.GetValue())[0])
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
        if dlg.ShowModal() == wx.ID_OK:
            ds = list(zip(*dlg.GetValue())[0])
            dlg.Destroy()

            sns.boxplot(self.parent.data[ds])
            plt.show()

    def createViolin(self, event):
        dlg = GraphDialog(self.parent, "Violinplot Input", ("Select Data",),
                size=(500, 200))
        if dlg.ShowModal() == wx.ID_OK:
            ds = list(zip(*dlg.GetValue())[0])
            dlg.Destroy()

            # TODO Allow user input for bandwidth
            sns.violinplot(self.parent.data[ds])
            plt.show()

    def createQQ(self, event):
        dlg = GraphDialog(self.parent, "QQ Plot Input", ("Select Data",),
                size=(700, 200), add=False)
        dists = [dist for dist in dir(stats.distributions) 
                if dist + "_gen" in dir(stats.distributions) and "_" not in dist]

        dlg.Add(wx.StaticText(dlg, label="Select Distribution"))
        dist = wx.ComboBox(dlg, 1, choices=dists, 
                  style=wx.CB_DROPDOWN | wx.CB_READONLY)
        dist.SetValue("norm")
        dlg.Add(dist)

        if dlg.ShowModal() == wx.ID_OK:
            ds = list(zip(*dlg.GetValue())[0])
            dist = dist.GetValue()
            pdf = stats.distributions.__dict__[dist] #hacky, but works
            dlg.Destroy()


            for d in ds:
                data = self.parent.data[d]
                data = data[np.isfinite(data)]
                stats.probplot(data, pdf.fit(data), dist, plot=plt)
            plt.show()

    def createTime(self, event):
        dlg = GraphDialog(self.parent, "Time Series Input", ("Select Data",), 
                size=(500, 200))

        if dlg.ShowModal() == wx.ID_OK:
            ds = list(zip(*dlg.GetValue())[0])
            dlg.Destroy()

            self.parent.data[ds].plot()
            plt.show()

    def createScatter(self, event):
        dlg = GraphDialog(self.parent, "Scatterplot Input", ("X", "Y"),
                size=(700, 200))
        regress = wx.CheckBox(dlg, label="Add Regression Polynomial?")
        regress.SetValue(True)
        ci = dlg.AddSpinCtrl("Confidence (>=100 for None)", 0, 101, 95)
        order = dlg.AddSpinCtrl("Polynomial Degree", 1, 10, 1)

        regress.Bind(wx.EVT_CHECKBOX, 
            lambda e: ci.Enable(regress.GetValue()) and order.Enable(regress.GetValue()))
        dlg.Add(regress)

        if dlg.ShowModal() == wx.ID_OK:
            ds = dlg.GetValue()
            dlg.Destroy()
            regress, ci, order = regress.GetValue(), ci.GetValue(), order.GetValue()

            data = self.parent.data[list({b for bs in ds for b in bs})].astype(float)
            snData = pd.DataFrame()
            for x, y in ds: # Deals with silly SNS stuff
                d = {"x":data[x], "y":data[y], "group":np.repeat(y, len(data[x]))}
                d = pd.DataFrame(d)
                snData = snData.append(d, ignore_index=True)

            try:
                if ci < 100 and regress:
                    sns.lmplot("x", "y", snData, color="group", ci=ci, order=order)
                else:
                    sns.lmplot("x", "y", snData, fitRegress=regress, ci=None, order=order)
                plt.show()
            except np.RankWarning:
                dlg = wx.MessageDialog(self.parent, "Polynomial Degree Too High",
                        style = wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                plt.show()

    def createMatrix(self, event):
        # TODO Fix ugly gridlines. sns.setStyle('nogrid') failed
        dlg = GraphDialog(self.parent, "Matrix Plot Input", ("Select Data",), 
                size=(500, 200))

        if dlg.ShowModal() == wx.ID_OK:
            ds = list(zip(*dlg.GetValue())[0])
            dlg.Destroy()

            pd.tools.plotting.scatter_matrix(self.parent.data[ds])
            plt.show()

    def createInteraction(self, event):
        dlg = GraphDialog(self.parent, "Matrix Plot Input", ("X1", "X2", "Y"),
                size=(700, 200), add=False)
        fill = wx.CheckBox(dlg, label="Fill")
        fill.SetValue(True)
        dlg.Add(fill)

        if dlg.ShowModal() == wx.ID_OK:
            (x1, x2, y), fill = dlg.GetValue(), fill.GetValue()
            data = self.parent.data[list({b for bs in ds for b in bs})].astype(float)
            dlg.Destroy()

            temp = data[[x1, x2, y]].dropna(axis=0)
            sns.interactplot(x1, x2, y, temp, cmap="coolwarm", filled=fill)

            plt.show()
    def createBiDensity(self, event):
        dlg = GraphDialog(self.parent, "Bivariate Density Fit", ("X1", "X2"),
                size=(700, 200))
        fill = wx.CheckBox(dlg, label="Fill")
        dlg.Add(fill)

        if dlg.ShowModal() == wx.ID_OK:
            ds, fill = dlg.GetValue(), fill.GetValue()
            data = self.parent.data[list({b for bs in ds for b in bs})].astype(float)
            dlg.Destroy()

            for x1, x2 in ds:
                temp = data[[x1, x2]].dropna(axis=0)
                sns.kdeplot(temp)
            plt.show()

