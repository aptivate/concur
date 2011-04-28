#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

try:
    import wx
except ImportError:
    raise ImportError,"The wxPython module is required to run this program"

class Device(object):
    def __init__(self, name, size):
        self._name = name
        self._size = size
        
    @property
    def name(self):
        return self._name

    @property
    def size(self):
        return self._size
    
    def humanSize(self):
        value = self._size
        units = "bytes"
        
        if value > 2000:
            value = value / 1000
            units = "kB"
            
        if value > 2000:
            value = value / 1000
            units = "MB"
           
        if value > 2000:
            value = value / 1000
            units = "GB"
        
        return "%.1f %s" % (value, units)

class MainWindow(wx.Frame):
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,id,title)
        self.parent = parent
        self.readPartitions()
        self.initialize()

    def readPartitions(self):
        p = open('/proc/partitions', 'r')
        p.readline() # discard
        p.readline() # discard
        self.devices = list()
        
        for line in p:
            found = re.match(r"""(?x) # allow whitespace and comments
                \s* # spaces at the beginning of the line
                (\d+) # first number, major device number
                \s+ # more spaces
                (\d+) # second number, minor device number
                \s+ # more spaces
                (\d+) # third number, device size in blocks
                \s+ # more spaces
                (\S+) # device name without /dev/
                \s* # optional spaces 
                \n # newline left in by readline()""",
                line)
            
            if not found:
                raise StandardError('Unknown line format in ' +
                    '/proc/partitions: ' + line)
            
            self.devices.append(Device(found.group(4),
                int(found.group(3)) * 1024))
        
    def addWithLabel(self, label, control, position):
        self.gridSizer.Add(wx.StaticText(self, label=label), position,
            flag=wx.ALIGN_CENTER_VERTICAL)
        self.gridSizer.Add(control, (position[0], position[1] + 1),
            flag=wx.EXPAND)
        return control

    def addChoiceControl(self, label, choices, position):
        choiceControl = wx.Choice(self, choices=choices)
        self.addWithLabel(label, choiceControl, position)
        return choiceControl
        
    def addSourceOrDestOptions(self, column, isDestination):
        types = ('Local Disk/Partition', 'Image File', 'FTP Server', 'SSHFS Server',
            'Windows/Samba Server', 'Multicast Network')
        typeBox = self.addChoiceControl('Type', types, (1, column))
        
        devBox = self.addChoiceControl('Device',
            ["%s (%s)" % (dev.name, dev.humanSize()) for dev in self.devices],
            (2, column))

        if isDestination:
            flpStyle = wx.FLP_OPEN | wx.FLP_OVERWRITE_PROMPT
        else:
            flpStyle = wx.FLP_OPEN | wx.FLP_FILE_MUST_EXIST
        
        imageFileBox = self.addWithLabel('Image File',
            wx.FilePickerCtrl(self, wildcard="Image files (*.img)|*.img",
                style=flpStyle), (3, column))

    def initialize(self):
        self.colSizer = wx.BoxSizer(orient=wx.VERTICAL)
        borderWidth = 10
        colFlags = wx.SizerFlags(0).Border(wx.ALL, borderWidth).Expand()
        
        self.presetList = wx.Choice(self, choices=('Clone disk to disk',
            'Backup disk to network', 'Restore disk from network',
            'Backup partition to network', 'Restore partition from network',
            'Wipe disk'))
        self.colSizer.AddF(self.presetList, colFlags)
        
        self.gridSizer = wx.GridBagSizer(6, 6)
        self.colSizer.AddF(self.gridSizer, colFlags.Proportion(1))
        
        self.gridSizer.Add(wx.StaticText(self, label='Source'), (0,0), (1,2),
            flag=wx.ALIGN_CENTER)
        self.gridSizer.Add(wx.StaticText(self, label='Method'), (0,2), (1,2),
            flag=wx.ALIGN_CENTER)
        self.gridSizer.Add(wx.StaticText(self, label='Destination'), (0,4), (1,2),
            flag=wx.ALIGN_CENTER)

        self.addSourceOrDestOptions(0, False)
        self.addSourceOrDestOptions(4, True)

        method_choices = ('Raw copy', 'Smart partition copy',
            'MBR copy')

        self.methodList = self.addChoiceControl('Method',
            method_choices, (1,2))
        
        self.buttonSizer = wx.StdDialogButtonSizer()
        self.colSizer.AddF(self.buttonSizer, colFlags.Proportion(0))
        
        self.startButton = wx.Button(self, id=wx.ID_OK)
        self.buttonSizer.Add(self.startButton)
        self.buttonSizer.SetAffirmativeButton(self.startButton)
        
        self.SetSizerAndFit(self.colSizer)
        self.Show(True)

if __name__ == "__main__":
    app = wx.App()
    frame = MainWindow(None, -1, 'Concur')
    app.MainLoop()
