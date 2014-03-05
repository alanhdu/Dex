import wx

class ColumnSelect(wx.Panel):
    orient, queries, parent, columns, names = None, None, None, None, None
    sizer = None
    def __init__(self, parent, data, queries, add=True, orient=wx.HORIZONTAL):
        wx.Panel.__init__(self, parent)
        self.parent, self.columns, self.queries = parent, [], queries
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.names = data.names()

        if add:
            new = wx.Button(self, -1, "+ More Data Sets")
            new.Bind(wx.EVT_BUTTON, self.moreChoices)
            self.sizer.Add(new)

        self.orient = orient
        self.SetSizer(self.sizer)
        self.moreChoices(None)

    def moreChoices(self, event):
        hsize = wx.BoxSizer(self.orient)
        new = []
        for i, q in enumerate(self.queries):
            new.append(wx.ComboBox(self, i, choices=list(self.names),
                style=wx.CB_DROPDOWN | wx.CB_READONLY))
            hsize.Add(wx.StaticText(self, label=q))
            hsize.Add(new[-1])
            hsize.AddSpacer(5)
        self.columns.append(tuple(new))
        self.sizer.Add(hsize)

        self.Layout()

    def onClose(self, event):
        self.Close(True)

    def GetValue(self):
        return [tuple(d.GetValue() for d in c) for c in self.columns]

# TODO implement some kind of global graph preferences
class GraphDialog(wx.Dialog):
    hsize, options, cs = None, None, None
    def __init__(self, parent, title, queries, size=wx.DefaultSize, add=True):
        wx.Dialog.__init__(self, parent, -1, title, size=size)
        self.cs = ColumnSelect(self, parent.data, queries, add=add)
        self.options = wx.BoxSizer(wx.VERTICAL)

        vsize = wx.BoxSizer(wx.VERTICAL)
        self.hsize = wx.BoxSizer(wx.HORIZONTAL)
        self.hsize.Add(self.options)
        self.hsize.AddSpacer(10)
        self.hsize.Add(self.cs, 1, wx.EXPAND)
        vsize.Add(self.hsize, 1, wx.EXPAND)

        vsize.Add(self.CreateSeparatedButtonSizer(flags=wx.OK | wx.CANCEL))
        self.SetSizer(vsize)
        self.Centre()

    def onClose(self, event):
        self.Close()
    def Add(self, *args):
        self.options.Add(*args)
        self.options.Layout()
        self.Layout()
    def AddSpinCtrl(self, label, min, max, initial=0, size=wx.DefaultSize):
        hsize = wx.BoxSizer(wx.HORIZONTAL)
        hsize.Add(wx.StaticText(self, label=label))
        ctrl = wx.SpinCtrl(self, min=min, max=max, initial=initial, size=size)
        hsize.Add(ctrl, flag=wx.ALIGN_RIGHT)
        self.Add(hsize)
        return ctrl
    def GetValue(self):
        return self.cs.GetValue()

class SummaryStats(wx.Panel):
    sizer, statitics = None, None
    def __init__(self, parent, stats, num=1, size=wx.DefaultSize):
        wx.Panel.__init__(self, parent, size=size)
        self.sizer, self.statistics = wx.GridSizer(num + 1, len(stats)), []

        for q in stats:
            self.sizer.Add(wx.StaticText(self, label=q))
        for i in xrange(num):
            temp = []
            for q in stats:
                temp.append(wx.TextCtrl(self, style=wx.TE_LEFT))
                self.sizer.Add(temp[-1])
            self.statistics.append(tuple(temp))
        self.SetSizer(self.sizer)
    def GetValue(self):
        return [[s.GetValue() for s in ss]
                for ss in self.statistics]
    def Enable(self, b):
        for ss in self.statistics:
            for s in ss:
                s.Enable(b)

class SampleStats(wx.Panel):
    sizer, samples = None, None
    def __init__(self, parent, choices, queries=None, num=1, size=wx.DefaultSize):
        wx.Panel.__init__(self, parent, size=size)
        if queries is None:
            queries = []

        self.sizer = wx.GridSizer(num + 1, len(queries) + 1)
        self.samples = []
        self.sizer.Add(wx.StaticText(self, label="Sample"))
        for q in queries:
            self.sizer.Add(wx.StaticText(self, label=q))
        for i in xrange(num):
            temp = []
            cb = wx.ComboBox(self, -1, choices=list(choices), size=(150,-1),
                    style=wx.CB_READONLY | wx.CB_DROPDOWN)
            self.sizer.Add(cb)
            temp.append(cb)
            for q in queries:
                temp.append(wx.TextCtrl(self, style=wx.TE_LEFT))
                self.sizer.Add(temp[-1])
            self.samples.append(temp)
        self.SetSizer(self.sizer)

    def GetValue(self):
        return  [[g.GetValue() for g in sample]
                  for sample in self.samples]
    def Enable(self, b):
        for samp in self.samples:
            for s in samp:
                s.Enable(b)


class StatTestDialog(wx.Dialog):
    hypo, Ho, stats, parent, samps = None, None, None, None, None
    sample, event = None, None

    def __init__(self, parent, title, statP=None, sampP=None, num=1, size=(700, 300)):
        wx.Dialog.__init__(self, parent, -1, title, size=size)
        self.parent = parent

        vsize = wx.BoxSizer(wx.VERTICAL)
        if statP is not None and sampP is not None:
            self.stats = SummaryStats(self, statP, num=num)
            self.samps = SampleStats(self, self.parent.data.names(), sampP,
                    num=num)

            self.sample = wx.RadioButton(self, label="Enter Samples")
            summary = wx.RadioButton(self, label="Enter Summary Statistics")
            self.sample.SetValue(True)
            self.stats.Enable(False)
            self.sample.Bind(wx.EVT_RADIOBUTTON, self.onSample)
            summary.Bind(wx.EVT_RADIOBUTTON, self.onSummary)

            dataP = wx.BoxSizer(wx.HORIZONTAL)
            vsizeL = wx.BoxSizer(wx.VERTICAL)
            vsizeL.Add(summary)
            vsizeL.Add(self.stats)

            vsizeR = wx.BoxSizer(wx.VERTICAL)
            vsizeR.Add(self.sample)
            vsizeR.Add(self.samps)

            dataP.Add(vsizeL, 1)
            dataP.AddSpacer(20)
            dataP.Add(vsizeR, 1)
        else:
            self.sample = sampP is not None
            if sampP is not None:
                self.samps = SampleStats(self, self.parent.data.names(), sampP,
                        num=num)
                dataP = self.samps
            if statP is not None:
                self.stats = SummaryStats(self, statP, num=num)
                dataP = self.stats

        vsize.Add(dataP, 1, wx.EXPAND)
        self.SetSizer(vsize)
        self.Centre()

        hsize = wx.BoxSizer(wx.HORIZONTAL)

        vsize1 = wx.BoxSizer(wx.VERTICAL)
        self.hypo = wx.CheckBox(self, label="Hypothesis Test?")
        self.hypo.Bind(wx.EVT_CHECKBOX, self.onHypothesis)
        vsize1.Add(self.hypo)

        hsize1 = wx.BoxSizer(wx.HORIZONTAL)
        hsize1.Add(wx.StaticText(self, label="H_o ="))
        self.Ho = wx.TextCtrl(self, style=wx.TE_LEFT)
        self.Ho.Enable(False)
        hsize1.Add(self.Ho, 1, wx.EXPAND)
        vsize1.Add(hsize1)

        hsize.Add(vsize1)
        hsize.AddSpacer(50)
        hsize.Add(wx.StaticText(self, label="Confidence (%): "))
        self.c = wx.SpinCtrl(self, min=1, max=99, initial=95)
        hsize.Add(self.c)

        vsize.Add(hsize)

        vsize.Add(self.CreateSeparatedButtonSizer(flags=wx.OK | wx.CANCEL))

    def GetValue(self):
        out = None
        try:
            self.sample = self.sample.GetValue()
        except AttributeError:
            pass
        if not self.sample: #summary statistics
            out = self.stats.GetValue()
        else:
            out = self.samps.GetValue()

        if self.hypo.GetValue():
            return (out, float(self.Ho.GetValue()), float(self.c.GetValue()))
        else:
            return (out, None, float(self.c.GetValue()))

    def onHypothesis(self, event):
        self.Ho.Enable(self.hypo.GetValue())
    def onSample(self, event):
        self.samps.Enable(True)
        self.stats.Enable(False)
    def onSummary(self, event):
        self.samps.Enable(False)
        self.stats.Enable(True)
