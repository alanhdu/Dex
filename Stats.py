import wx
from Data import Data
from Dialogues import GraphDialog, StatTestDialog, SampleStats, SummaryStats
import numpy as np
from scipy import stats
from matplotlib import pyplot as plt
import seaborn as sns

class StatsMenu(wx.Menu):
    parent = None
    def __init__(self, parent):
        wx.Menu.__init__(self)
        self.parent = parent

        parent.Bind(wx.EVT_MENU, self.describe, 
                self.Append(wx.NewId(), "Descriptive Statistics"))
        self.AppendSeparator()

        # basic tests
        parent.Bind(wx.EVT_MENU, self.ztest1, 
                self.Append(wx.NewId(), "1-Proportion Z-test"))
        parent.Bind(wx.EVT_MENU, self.ztest2, 
                self.Append(wx.NewId(), "2-Proportion Z-test"))
        parent.Bind(wx.EVT_MENU, self.ttest1, 
                self.Append(wx.NewId(), "1-Sample T-test"))
        parent.Bind(wx.EVT_MENU, self.ttest2, 
                self.Append(wx.NewId(), "2-Sample T-test"))
        parent.Bind(wx.EVT_MENU, self.ttest_matched, 
                self.Append(wx.NewId(), "Matched-Pair T-test"))

        # Regression


        # Nonparametric tests


        # Bayesian Inference

    def describe(self, event):
        dlg = GraphDialog(self.parent, "Descriptive Statistics", 
                ("Select Data",), add=False)

        if dlg.ShowModal() == wx.ID_OK:
            d = dlg.GetValue()[0][0]
            data = self.parent.data[d].dropna(axis=0)

            mean, std = data.mean(), data.std()
            median = np.median(data)
            q1, q3 = np.percentile(data, 25), np.percentile(data, 75)
            template1 = "{:<10}" * 6 + "\n"
            template2 = "{:<10.4g}" * 6 + "\n"

            out = template1.format("Mean", "Std Dev", "Q1", "Med", "Q3", "IQR")
            out += template2.format(mean, std, q1, median, q3, q3-q1)

            self.parent.output.AppendText("\nDescriptive Statistics for " + d)
            self.parent.output.AppendText("\n" + out)

        dlg.Destroy()

    # TODO Maybe rewrite so it uses binomial distribution instead of normal approximation?
    def ztest1(self, event):
        dlg = StatTestDialog(self.parent, "1-Proportion Z-Test", 
                statP=("# of Trials", "# of Events"), sampP=("Event",))
        if dlg.ShowModal() == wx.ID_OK:
            info, p_o, c = dlg.GetValue()
            info, n, count, c = info[0], 0, 0, float(c) / 100
            name = None

            try: # works for summary statistics
                n, count = int(info[0]), int(info[1])
            except ValueError:
                name, evt = info
                data = self.parent.data[name].dropna()
                n , count = len(data), len(data[data == evt])

            if count < 10 or n - count < 10:
                d = wx.MessageDialog(self.parent, style=wx.OK|wx.ICON_WARNING,
                        message="Warning: Data might not be sufficiently normal")
                d.ShowModal()
                d.Destroy()

            pHat = float(count) / n
            se = np.sqrt(pHat * (1-pHat) / n)
            z = stats.norm.ppf(0.5 + 0.5 * c) # two-tailed test
            ci = "({:.3%}, {:.3%})".format(pHat-z*se, pHat + z*se)

            headerTemp = "{:<9} {:<7} {:<8} {:^20}"
            statsTemp = "{:<9} {:<7} {:<8.3%} {:^20}"
            header = headerTemp.format("Observed", "N", "pHat", "{:.1%} CI".format(c)) 
            st = statsTemp.format(count, n, pHat, ci)

            if p_o is not None:
                se_o = np.sqrt(p_o * (1-p_o) / n)
                z_o = (pHat - p_o) / se_o
                
                p_value = 2 * (1 - stats.norm.cdf(abs(z_o)))
                header += "{:<10} {:<10} {:<10}".format("p_o", "z score", "p-value")
                st += "{:<10.3f} {:<10.3f} {:<10.4f}".format(p_o, z_o, p_value)

            title = "\n1-Proportion Z-Test"
            if name is not None:
                title += " for {}".format(name)
            self.parent.output.AppendText("\n".join([title, header, st]) + "\n")
        dlg.Destroy()
    def ztest2(self, event):
        dlg = StatTestDialog(self.parent, "2-Proportion Z-Test", 
                statP=("# of Trials", "# of Events"), sampP=("Event",), num=2)
        dlg.hypo.SetValue(True)
        dlg.hypo.Enable(False)
        dlg.Ho.SetValue('0')
        dlg.Ho.Enable(False)
        if dlg.ShowModal() == wx.ID_OK:
            info, p_o, c = dlg.GetValue()
            c /= 100.0
            names = None

            try:
                n1, count1 = int(info[0][0]), int(info[0][1])
                n2, count2 = int(info[1][0]), int(info[1][1])
            except ValueError:
                d1, evt1 = info[0]
                d2, evt2 = info[1]
                names = (d1, d2)
                data1, data2 = self.parent.data[d1].dropna(), self.parent.data[d2].dropna()
                n1 , count1 = len(data1), len(data1[data1 == evt1])
                n2 , count2 = len(data2), len(data2[data2 == evt2])

            pHat1, pHat2 = float(count1)/n1, float(count2)/n2
            se = np.sqrt(pHat1 * (1-pHat1) / n1 + (pHat2 * (1-pHat2)) / n2)
            z = stats.norm.ppf(0.5 + 0.5 * c)
            diffPHat = pHat1 - pHat2
            ci = "({:.3%}, {:.3%})".format(diffPHat-z*se, diffPHat + z*se)

            header = "{:<3} {:<9} {:<7} {:<8}\n".format("#", "Observed", "N", "pHat")
            statsTemp = "{:<3} {:<9} {:<7} {:<8.3%}\n"
            st = statsTemp.format(1, count1, n1, pHat1, ci) 
            st += statsTemp.format(2, count2, n2, pHat2, ci)

            output = header + st

            header = "{:^22} ".format("{:.1%} CI".format(c))
            st = "\n{:^22} ".format(ci)

            if p_o is not None:
                p_pooled = (count1+count2) / float(n1 + n2)
                se_o = np.sqrt( p_pooled * (1-p_pooled) * (1/float(n1) + 1/float(n2)))
                z_o = diffPHat / se_o
                p_value = 2 * (1 - stats.norm.cdf(abs(z_o)))
                header += "{:<10} {:<10}".format("z score", "p-value")
                st += "{:<10.3f} {:<10.4f}\n".format(z_o, p_value)

            output += header + st

            title = "\n2-Proportion T-Test"
            if names is not None:
                title += " Between {} and {}".format(names[0], names[1])
            self.parent.output.AppendText(title + "\n" + output)

        dlg.Destroy()
    def ttest1(self, event):
        dlg = StatTestDialog(self.parent, "1-Sample T-Test", 
                statP=("Sample Size", "Mean", "Std Dev"), sampP=())
        if dlg.ShowModal() == wx.ID_OK:
            info, x_o, c = dlg.GetValue()
            info, c = info[0], float(c) / 100
            name = None

            try: # works for summary statistics
                n, mean, std = int(info[0]), float(info[1]), float(info[2])
            except ValueError:
                data = self.parent.data[info[0]].dropna()
                name = info[0]
                n, mean, std = len(data), data.mean(), data.std()

            se = std / np.sqrt(n)
            t = stats.t.ppf(0.5 + 0.5 * c, n-1)
            ci = "({:.4f}, {:.4f})".format(mean-t*se, mean + t*se)

            headerTemp = "{:<7} {:<10} {:<10} {:^22}"
            statsTemp = "{:<7} {:<10.3f} {:<10.3f} {:^22}"
            header = headerTemp.format("N", "Mean", "Std Dev", "{:.1%} CI".format(c)) 
            st = statsTemp.format(n, mean, std, ci)

            if x_o is not None:
                t = (mean - x_o) / se
                p = 2 * (1 - stats.t.cdf(abs(t), n-1))

                # TODO Figure out Greek Letters, fancy notation (e.g. x-bar, subscript)
                header += "{:<10} {:<10} {:<10}".format("mu_o", "t score", "p-value")
                st += "{:<10.3f} {:<10.3f} {:<10.4f}".format(x_o, t, p)


            title = "\n1-Sample T-Test"
            if name is not None:
                title += " for {}".format(name)
            self.parent.output.AppendText("\n".join([title, header, st]) + "\n")
        dlg.Destroy()

    def ttest2(self, event):
        dlg = StatTestDialog(self.parent, "2-Sample T-Test", num=2,
                statP=("Sample Size", "Mean", "Std Dev"), sampP=())
        dlg.hypo.SetValue(True) # force hypothesis test
        dlg.hypo.Enable(False)
        dlg.Ho.SetValue('0')
        dlg.Ho.Enable(False)
        if dlg.ShowModal() == wx.ID_OK:
            info, x_o, c = dlg.GetValue()
            names = None
            c = float(c) / 100

            try: # works for summary statistics
                n1, mean1, std1 = int(info[0][0]), float(info[0][1]), float(info[0][2])
                n2, mean2, std2 = int(info[1][0]), float(info[1][1]), float(info[1][2])
            except ValueError:
                ds = self.parent.data[info[0] + info[1]]
                names = info[0][0], info[1][0]
                data1, data2 = ds[info[0][0]].dropna(), ds[info[1][0]].dropna()
                n1, mean1, std1 = len(data1), data1.mean(), data1.std()
                n2, mean2, std2 = len(data2), data2.mean(), data2.std()
            se1, se2 = std1 / np.sqrt(n1), std2 / np.sqrt(n2)
            se = np.sqrt(se1*se1 + se2*se2)

            temp1 = std1*std1 / n1
            temp2 = std2*std2 / n2
            df = (temp1 + temp2) ** 2 / (temp1 * temp1 / (n1-1) + temp2 * temp2 / (n2-1))
            t = stats.t.ppf(0.5 + 0.5 * c, df)
            ci = "({:.4f}, {:.4f})".format(mean1-mean2 - t*se, mean1-mean2 + t*se)

            header = "{:<5} {:<7} {:<9} {:<9} {:<9}\n".format("#", "N", "Mean", "Std Dev", "Std Error")
            statsTemp = "{:<5} {:<7} {:<9.3f} {:<9.3f} {:<9.3f}\n"
            st = statsTemp.format(1, n1, mean1, std1, se1) + statsTemp.format(2, n2, mean2, std2, se2)
            output = "\n" + header + st

            t = (mean1 - mean2) / se
            p = 2 * (1 - stats.t.cdf(abs(t), df))
            header = "{:^20} {:<10} {:<10} {:<10}\n".format("{:.1%} CI".format(c),
                    "t_score", "DF", "p-value")
            st = "{:^20} {:<10.3f} {:<10.3f} {:<10.4f}\n".format(ci, t, df, p)

            output += header + st + "\n"
            title = "\n2-Sample T-Test"
            if names is not None:
                title += " Between {} and {}".format(names[0], names[1])
            self.parent.output.AppendText(title + output)
        dlg.Destroy()
    def ttest_matched(self, event):
        dlg = StatTestDialog(self.parent, "Matched Pair T-Test", num=2,
                statP=None, sampP=())
        # TODO funky spacings when statP=None

        dlg.hypo.SetValue(True) # force hypothesis test
        dlg.hypo.Enable(False)
        dlg.Ho.SetValue('0')
        dlg.Ho.Enable(False)
        if dlg.ShowModal() == wx.ID_OK:
            info, x_o, c = dlg.GetValue()
            c = float(c) / 100

            data1 = self.parent.data[info[0][0]]
            data2 = self.parent.data[info[1][0]]
            data = (data1 - data2).dropna()
            n, mean, std = len(data), data.mean(), data.std()

            se = std / np.sqrt(n)
            t = stats.t.ppf(0.5 + 0.5 * c, n-1)
            ci = "({:.4f}, {:.4f})".format(mean-t*se, mean + t*se)

            headerTemp = "{:<7} {:<10} {:<10} {:^22} "
            statsTemp = "{:<7} {:<10.3f} {:<10.3f} {:^22} "
            header = headerTemp.format("N", "Mean", "Std Dev", "{:.1%} CI".format(c)) 
            st = statsTemp.format(n, mean, std, ci)

            t = (mean - x_o) / se
            p = 2 * (1 - stats.t.cdf(abs(t), n-1))

            header += "{:<10} {:<10}".format("t score", "p-value")
            st += "{:<10.3f} {:<10.4f}".format(t, p)
            output = "\nMatched Pair T-Test Between {} and {}\n{}\n{}\n"
            self.parent.output.AppendText(output.format(info[0][0], info[1][0], header, st))

            sns.distplot(data.astype(float), 
                    kde_kws={"label":"{0} - {1}".format(info[0][0], info[1][0])})
            plt.show()
        dlg.Destroy()
