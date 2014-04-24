import wx

class ColumnSelect(wx.Panel):
    queries, parent, columns, names, sNames = None, None, None, None, None
    sizer = None
    def __init__(self, parent, data, queries, add=True):
        wx.Panel.__init__(self, parent)
        self.parent, self.columns, self.queries = parent, [], queries

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.names = data.names()
        # prevent overflow errors with long name lengths
        self.sNames = [len(n) < 20 and n or n[:20] + "..." for n in self.names]

        if add:
            new = wx.Button(self, -1, "+ More Data Sets")
            new.Bind(wx.EVT_BUTTON, self.moreChoices)
            self.sizer.Add(new)
        else:
            # insert button's height of space
            self.sizer.AddSpacer(wx.Button.GetDefaultSize()[1])

        hsize = wx.GridSizer(cols=len(self.queries))
        for q in self.queries:
            hsize.Add(wx.StaticText(self, label=q))
        self.sizer.Add(hsize, flag=wx.EXPAND)

        self.SetSizer(self.sizer)
        self.moreChoices(None)

    def moreChoices(self, event):
        hsize = wx.GridSizer(cols=len(self.queries))
        new = []
        for q in self.queries:
            new.append(wx.ComboBox(self, choices=[""] + self.sNames,
                style=wx.CB_DROPDOWN | wx.CB_READONLY))
            hsize.Add(new[-1], 1, flag=wx.EXPAND)
        self.columns.append(tuple(new))
        self.sizer.Add(hsize)

        self.parent.Layout()

    def onClose(self, event):
        self.Close(True)
    def get(self, abbrev):
        return self.names[self.sNames.index(abbrev)]

    def GetValue(self):
        return [tuple(self.get(d.GetValue()) for d in c) for c in self.columns]

# TODO implement some kind of global graph preferences
class GraphDialog(wx.Dialog):
    group, hsize, options, cs = None, None, None, None
    def __init__(self, parent, title, queries, size=wx.DefaultSize, add=True, groups=True):
        wx.Dialog.__init__(self, parent, -1, title, size=size)
        self.cs = ColumnSelect(self, parent.data, queries, add=add)
        self.options = wx.BoxSizer(wx.VERTICAL)
        if groups:
            self.group = ColumnSelect(self, parent.data, ["Group by"], add=False)
            self.options.Add(self.group)
        else:
            self.group = None

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
    def Add(self, *args, **kwargs):
        self.options.Add(*args, **kwargs)
        self.options.Layout()
        self.Layout()
    def AddSpinCtrl(self, label, min, max, initial=0, size=wx.DefaultSize):
        hsize = wx.BoxSizer(wx.HORIZONTAL)
        hsize.Add(wx.StaticText(self, label=label))
        ctrl = wx.SpinCtrl(self, min=min, max=max, initial=initial, size=size)
        hsize.Add(ctrl, flag=wx.ALIGN_RIGHT)
        self.Add(hsize)
        return ctrl
    def GetValue(self, data):
        val = []
        group = self.GetGroup()
        if group:
            columns = self.GetName()
            df = data[ [item for sub in columns for item in sub] + [group] ]
            grouped=  df.groupby(group)
            for cs in columns:
                val += [grouped.get_group(g)[list(cs)] for g in grouped.groups]
            g = [str(g) for g in grouped.groups]
        else:
            for cs in self.GetName():
                val.append(data[list(cs)])
        return g, val
    def GetName(self):
        return self.cs.GetValue()
    def GetGroup(self):
        if self.group:
            return self.group.GetValue()[0][0]
        else:
            return None

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

class RegressDialog(wx.Dialog):
    parent, xs, y = None, None, None
    def __init__(self, parent, title, size=(700, 300)):
        wx.Dialog.__init__(self, parent, -1, title, size=size)
        self.parent = parent
        self.xs = ColumnSelect(self, parent.data, 
                queries=("Select Explanatory Variable(s)",), add=True)
        self.y = ColumnSelect(self, parent.data, 
                    queries=("Select Dependent Variable",), add=False)

        vsize = wx.BoxSizer(wx.VERTICAL)
        hsize = wx.BoxSizer(wx.HORIZONTAL)
        hsize.Add(self.y, 1, wx.EXPAND)
        hsize.AddSpacer(10)
        hsize.Add(self.xs, 1, wx.EXPAND)

        vsize.Add(hsize)

        vsize.Add(self.CreateSeparatedButtonSizer(flags=wx.OK | wx.CANCEL))
        self.SetSizer(vsize)

    def GetValue(self):
        return (self.y.GetValue()[0][0], zip(*self.xs.GetValue())[0])
