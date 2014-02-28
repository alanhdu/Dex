import numpy as np
import wx

class Data():
    parent, names, data = None, None, None
    
    def __init__(self, filename, parent):
        self.parent = parent
        self.names = {}
        self.data = np.genfromtxt(filename, delimiter=",", names=True)
        print filename
        labels = self.data.dtype.names

        for i, label in enumerate(labels):
            self.names[label] = i

        # data in colums not rows
        self.data = np.genfromtxt(filename, delimiter=",").transpose()
        self.data = self.data[:,1:]  # ignore headers
    def __getitem__(self, key):
        print "Goodbye ", key
        try:
            return self.data[key]
        except ValueError: # assume key is string
            try:
                return self.data[self.names[key]]
            except KeyError:
                dlg = wx.MessageDialog(self.parent, "Invalid Column", 
                        style= wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
        except IndexError:
            dlg = wx.MessageDialog(self.parent, "Invalid Column", 
                    style= wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
