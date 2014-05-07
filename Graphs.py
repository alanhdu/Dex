import wx
from matplotlib import pyplot as plt
from Dialogues import GraphDialog, RegressDialog
from mpl_toolkits.mplot3d import Axes3D
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
        parent.Bind(wx.EVT_MENU, self.createMatrixInteract, 
                self.Append(wx.NewId(), "Matrix Interaction Plot"))

        # Multivariate
        self.AppendSeparator()
        parent.Bind(wx.EVT_MENU, self.createBiDensity, 
                self.Append(wx.NewId(), "Bivariate Density Fit"))
        parent.Bind(wx.EVT_MENU, self.create3DScatter,
                self.Append(wx.NewId(), "3D Scatter Plot"))


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
            ds = [d[0] for d in dlg.GetName()]
            # account for grouping
            groups, datas = dlg.GetValue(self.parent.data)
            bars, density = bars.GetValue(), density.GetValue() 
            bandwidth = np.exp(-0.2 * bandwidth.GetValue())
            if groups:
                ds = self._groupLabels(ds, groups)
                newDs = []
                for d in ds:
                    newDs += [d + "-" + str(g) for g in groups]
                ds = newDs
            dlg.Destroy()

            # d.min() gets minimum for each column. d.min.min() gets global min
            a, b = min(d.min().min() for d in datas), max(d.max().max() for d in datas)
            bins = np.arange(a, b, float(b-a) / numBins.GetValue())

            for d, data in zip(ds, datas):
                data = data[data.columns[0]]
                d, data = d, data.astype(float)
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
    
    def _groupLabels(self, labels, groups):
        new = []
        for l in labels:
            new += [l + "-" + str(g) for g in groups]
        return new

    def createBoxplot(self, event):
        dlg = GraphDialog(self.parent, "Boxplot Input", queries=("Select Data",),
                size=(500, 200))
        if dlg.ShowModal() == wx.ID_OK:
            ds = [d[0] for d in dlg.GetName()]
            groups, datas = dlg.GetValue(self.parent.data)
            if groups:
                ds = self._groupLabels(ds, groups)
            dlg.Destroy()

            sns.boxplot(datas, names=ds)
            plt.show()

    def createViolin(self, event):
        dlg = GraphDialog(self.parent, "Violinplot Input", ("Select Data",),
                size=(500, 200))
        if dlg.ShowModal() == wx.ID_OK:
            ds = [d[0] for d in dlg.GetName()]
            groups, datas = dlg.GetValue(self.parent.data)
            if groups:
                ds = self._groupLabels(ds, groups)

            # convert dataframe to series to avoid seaborn error
            for i in xrange(len(datas)):
                datas[i] = datas[i][datas[i].columns[0]]
            dlg.Destroy()

            # TODO Allow user input for bandwidth
            #sns.violinplot([self.parent.data[[ds[0]]]], names=ds)
            sns.violinplot(datas, names=ds)
            plt.show()

    def createQQ(self, event):
        dlg = GraphDialog(self.parent, "QQ Plot Input", ("Select Data",),
                size=(700, 200), add=False, groups=False)
        dists = [dist for dist in dir(stats.distributions) 
                if dist + "_gen" in dir(stats.distributions) and "_" not in dist]

        dlg.Add(wx.StaticText(dlg, label="Select Distribution"))
        dist = wx.ComboBox(dlg, 1, choices=dists, 
                  style=wx.CB_DROPDOWN | wx.CB_READONLY)
        dist.SetValue("norm")
        dlg.Add(dist)

        if dlg.ShowModal() == wx.ID_OK:
            ds = dlg.GetName()
            dist = dist.GetValue()
            pdf = stats.distributions.__dict__[dist] #hacky, but works
            dlg.Destroy()


            for d in (x[0] for x in ds):
                data = self.parent.data[d]
                data = data[np.isfinite(data)]
                stats.probplot(data, pdf.fit(data), dist, plot=plt)
            plt.show()

    def createTime(self, event):
        dlg = GraphDialog(self.parent, "Time Series Input", ("Select Data",), 
                size=(500, 200), groups=False)

        if dlg.ShowModal() == wx.ID_OK:
            ds = [x[0] for x in dlg.GetName()]
            dlg.Destroy()
            self.parent.data[ds].plot()
            plt.show()

    def createScatter(self, event):
        dlg = GraphDialog(self.parent, "Scatterplot Input", ("X", "Y"),
                size=(700, 200), groups=False)
        regress = wx.CheckBox(dlg, label="Add Regression Polynomial?")
        regress.SetValue(True)
        jitter = wx.CheckBox(dlg, label="Jitter?")
        jitter.SetValue(False)
        dlg.Add(jitter)
        ci = dlg.AddSpinCtrl("Confidence (>=100 for None)", 0, 101, 95)
        order = dlg.AddSpinCtrl("Polynomial Degree", 1, 10, 1)

        regress.Bind(wx.EVT_CHECKBOX, 
            lambda e: ci.Enable(regress.GetValue()) and order.Enable(regress.GetValue()))
        dlg.Add(regress)

        if dlg.ShowModal() == wx.ID_OK:
            ds = dlg.GetName()
            dlg.Destroy()
            regress, ci = regress.GetValue(), ci.GetValue()
            order, jitter = order.GetValue(), jitter.GetValue()

            data = self.parent.data[list({b for bs in ds for b in bs})].astype(float)
            snData = pd.DataFrame()
            for x, y in ds: # Deals with silly SNS stuff
                d = {"x":data[x], "y":data[y], "group":np.repeat(y, len(data[x]))}
                d = pd.DataFrame(d)
                snData = snData.append(d, ignore_index=True)

            if jitter:
                xjitter = snData["x"].std() / 4
                yjitter = snData["y"].std() / 4
            else:
                xjitter, yjitter = 0, 0

            try:
                if ci < 100 and regress:
                    sns.lmplot("x", "y", snData, hue="group", ci=ci, order=order, 
                            x_jitter=xjitter, y_jitter=yjitter)
                else:
                    sns.lmplot("x", "y", snData, fit_reg=regress, ci=None, order=order,
                            x_jitter=xjitter, y_jitter=yjitter)
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
                size=(500, 300), groups=False)

        if dlg.ShowModal() == wx.ID_OK:
            ds = [d[0] for d in dlg.GetName()]
            df = self.parent.data[ds]
            n = len(ds)
            dlg.Destroy()
                
            pd.scatter_matrix(df, grid=False)
            plt.show()
    def createMatrixInteract(self, event):
        dlg = RegressDialog(self.parent, "Matrix Interaction Plot") 
        log = wx.CheckBox(dlg, label="Logistic Fit?")
        dlg.Add(log)
        if dlg.ShowModal() == wx.ID_OK:
            y, xs = dlg.GetValue()
            log = log.GetValue()
            data = self.parent.data[list(xs) + [y]].dropna()
            df = data[list(xs)]

            fig, axes = plt.subplots(nrows=len(xs), ncols=len(xs))
            for i, l1 in enumerate(df):
                for j, l2  in enumerate(df):
                    ax = axes[j, i]
                    ax.grid(False)
                    plt.subplot(ax)
                    if i == j:
                        sns.regplot(data[l1], data[y], ax=ax),
                        # would like to do logistic plot, but takes too long
                    elif i < j:
                        sns.interactplot(l1, l2, y, data, ax=ax, logistic=log)
                    print j, i, l1, l2

                    if i != 0 and j != 0:
                        ax.yaxis.set_visible(False)
                    if j != len(xs) - 1:
                        ax.xaxis.set_visible(False)

            plt.show()

    def createInteraction(self, event):
        dlg = GraphDialog(self.parent, "Matrix Plot Input", ("X1", "X2", "Y"),
                size=(700, 200), add=False, groups=False)
        fill = wx.CheckBox(dlg, label="Fill")
        fill.SetValue(True)
        log = wx.CheckBox(dlg, label="Logistic Fit?")
        dlg.Add(fill)
        dlg.Add(log)

        if dlg.ShowModal() == wx.ID_OK:
            (x1, x2, y), fill = dlg.GetName()[0], fill.GetValue()
            log = log.GetValue()
            data = self.parent.data[[x1, x2, y]].astype(float)
            dlg.Destroy()

            temp = data[[x1, x2, y]].dropna(axis=0)
            sns.interactplot(x1, x2, y, temp, cmap="coolwarm", filled=fill,
                    logistic=log)

            plt.show()
    def createBiDensity(self, event):
        dlg = GraphDialog(self.parent, "Bivariate Density Fit", ("X1", "X2"),
                size=(700, 200), add=False, groups=False)
        fill = wx.CheckBox(dlg, label="Fill")
        dlg.Add(fill)

        if dlg.ShowModal() == wx.ID_OK:
            ds, fill = dlg.GetName(), fill.GetValue()
            data = self.parent.data[list({b for bs in ds for b in bs})].astype(float)
            dlg.Destroy()

            for x1, x2 in ds:
                temp = data[[x1, x2]].dropna(axis=0)
                sns.kdeplot(temp, shade=fill)
            plt.show()

    def create3DScatter(self, event):
        dlg = GraphDialog(self.parent, "3D Scatter Plot Fit", ("X1", "X2", "Y"),
                size=(700, 200), add=False, groups=False)

        if dlg.ShowModal() == wx.ID_OK:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection="3d")

            x1, x2, y = dlg.GetName()[0]
            data = self.parent.data[[x1, x2, y]]
            ax.scatter(data[x1], data[x2], data[y])
            plt.show()
