import wx

class ColumnSelect(wx.Dialog):
    parent, columns, = None, None
    def __init__(self, parent, id, title, queries):
        wx.Dialog.__init__(self, parent, id, title)
        self.parent = parent
        self.columns = [wx.ComboBox(self, i,choices=self.parent.data.names.keys(),
                    style=wx.CB_DROPDOWN | wx.CB_READONLY)
                   for i, q in enumerate(queries)]

        wx.Button(self, -1, "Ok")
        self.Centre()

    def onClose(self, event):
        self.Close(True)

    def GetValue(self):
        return [c.GetValue() for c in self.columns]
