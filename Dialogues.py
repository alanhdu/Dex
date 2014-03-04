import wx

class ColumnSelect(wx.Panel):
    queries, parent, columns, names = None, None, None, None
    sizer = None
    def __init__(self, parent, data, queries):
        wx.Panel.__init__(self, parent)
        self.parent, self.columns, self.queries = parent, [], queries
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.names = data.names()

        new = wx.Button(self, -1, "+")
        new.Bind(wx.EVT_BUTTON, self.moreChoices)
        self.sizer.Add(new)
        self.SetSizer(self.sizer)

        self.moreChoices(None)


    def moreChoices(self, event):
        hsize = wx.BoxSizer(wx.HORIZONTAL)
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

class GraphDialog(wx.Dialog):
    hsize, options, cs = None, None, None
    def __init__(self, parent, title, queries, size=wx.DefaultSize):
        wx.Dialog.__init__(self, parent, -1, title, size=size)
        self.cs = ColumnSelect(self, parent.data, queries)

        vsize = wx.BoxSizer(wx.VERTICAL)
        self.hsize = wx.BoxSizer(wx.HORIZONTAL)
        options = wx.Panel(self)
        self.hsize.Add(options)
        self.hsize.AddSpacer(10)
        self.hsize.Add(self.cs, 1, wx.EXPAND)

        vsize.Add(self.hsize, 1, wx.EXPAND)

        ok = wx.Button(self, -1, "OK")
        ok.Bind(wx.EVT_BUTTON, self.onClose)
        vsize.Add(ok)

        self.SetSizer(vsize)
    def onClose(self, event):
        self.Close()
    def Add(self, *args):
        self.options.Add(*args)
    def GetValue(self):
        return self.cs.GetValue()


