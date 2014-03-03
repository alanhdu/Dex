import wx

class ColumnSelect(wx.Panel):
    queries, parent, columns, names = None, None, None, None
    sizer = None
    def __init__(self, parent, data, queries):
        wx.Panel.__init__(self, parent)
        self.parent, self.columns, self.queries = parent, [], queries
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.names = data.names.keys()

        new = wx.Button(self, -1, "+")
        new.Bind(wx.EVT_BUTTON, self.moreChoices)
        self.sizer.Add(new)
        self.SetSizer(self.sizer)

        self.moreChoices(None)


    def moreChoices(self, event):
        for i, q in enumerate(self.queries):
            holder = wx.Panel(self)
            bs = wx.BoxSizer(wx.HORIZONTAL)
            bs.Add(wx.StaticText(holder, label=q))
            self.columns.append(wx.ComboBox(holder, i, choices=self.names,
                style=wx.CB_DROPDOWN | wx.CB_READONLY))
            bs.Add(self.columns[-1])
            holder.SetSizer(bs)

            self.sizer.Add(holder)
        self.Layout()

    def onClose(self, event):
        self.Close(True)

    def GetValue(self):
        return [c.GetValue() for c in self.columns]
