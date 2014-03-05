import numpy as np
import wx
import pandas as pd

class Data():
    parent, data = None, None
    def __init__(self, filename, parent):
        self.parent = parent
        if filename.endswith("csv"):
            # auto determine delimiter
            self.data = pd.read_csv(filename, delimiter=None, sep=None)  

    def __getitem__(self, key):
        try: 
            return self.data[key]
        except KeyError:
            try: 
                return self.data[self.data.columns[key]] #allow numerical access
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
