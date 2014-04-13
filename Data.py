import numpy as np
import wx
import wx.lib.sheet
import pandas as pd


class Data1(wx.lib.sheet.CSheet):
    parent, data = None, None
    def __init__(self, parent):
        wx.lib.sheet.CSheet.__init__(self, parent)
        self.SetNumberRows(0)
        self.SetNumberCols(0)
        self.data = pd.DataFrame()
    def readFile(self, filename):
        if filename.endswith("csv"):
            self.data = pd.read_csv(filename, delimiter=None, sep=None)
        rows, cols = self.data.shape
        self.SetNumberCols(cols)
        self.SetNumberRows(rows)
        self.fill()

    def fill(self):
        for i, name in enumerate(self.data.columns):
            self.SetColLabelValue(i, name)
            for j, val in enumerate(self.data[name]):
                self.SetCellValue(j, i, str(val))
    def __getitem__(self, key):
        try: 
            return self.data[key].dropna()
        except KeyError:
            try: 
                return self.data[self.data.columns[key]].dropna() #allow numerical access
            except (ValueError, IndexError):
                dlg = wx.MessageDialog(self.parent, "Invalid Column", 
                        style= wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                raise KeyError
    def __len__(self):
        return len(self.data)
    def names(self):
        return self.data.columns
    def min(self):
        return np.nanmin(self.data)
    def max(self):
        return np.nanmax(self.data)
    def shape(self):
        return self.data.shape
    def OnCellChange(self, evt):
        colName = self.GetColLabelValue(evt.Col)
        v = self.GetCellValue(evt.Row, evt.Col)
        t = self.data[colName].dtype.type
        print v, type(v)
        self.data.loc[evt.Row, colName] = t(v)

class Data():
    parent, data = None, None
    def __init__(self, filename, parent):
        self.parent = parent
        if filename.endswith("csv"):
            # auto determine delimiter
            self.data = pd.read_csv(filename, delimiter=None, sep=None)  

    def __getitem__(self, key):
        try: 
            return self.data[key].dropna()
        except KeyError:
            try: 
                return self.data[self.data.columns[key]].dropna() #allow numerical access
            except (ValueError, IndexError):
                dlg = wx.MessageDialog(self.parent, "Invalid Column", 
                        style= wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                raise KeyError
    def __len__(self):
        return len(self.data)
    def names(self):
        return self.data.columns
    def min(self):
        return np.nanmin(self.data)
    def max(self):
        return np.nanmax(self.data)
    def shape(self):
        return self.data.shape
