#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os
import subprocess

try:
    import wx
except ImportError:
    raise ImportError, "The wxPython module is required to run this program"

from wx.lib.agw.genericmessagedialog import GenericMessageDialog as MessageDialog

# http://www.win.tue.nl/~aeb/partitions/partition_types-1.html

partition_types = {
    0x01: "DOS 12-bit FAT (up to 16 MB)",
    0x02: "XENIX root",
    0x03: "XENIX /usr",
    0x04: "DOS 3.0+ 16-bit FAT (up to 32 MB)",
    0x05: "DOS 3.3+ Extended Partition (up to 8.4 GB)",
    0x06: "DOS 3.31+ 16-bit FAT (over 32 MB)",
    0x07: "NTFS/HPFS/FAT64/exFAT/Advanced Unix/QNX",
    0x08: "OS/2 (v1.0-1.3 only)/AIX boot/SplitDrive/DELL",
    0x09: "AIX data partition/Coherent fs",
    0x0a: "OS/2 Boot Manager/Coherent swap/OPUS",
    0x0b: "WIN95 OSR2 FAT32, non-LBA",
    0x0c: "WIN95 OSR2 FAT32, LBA-mapped",
    0x0e: "WIN95: DOS 16-bit FAT, LBA-mapped",
    0x0f: "WIN95: Extended partition, LBA-mapped",
    0x11: "Hidden (by OS/2) DOS 12-bit FAT/Leading Edge DOS 3.x",
    0x12: "Compaq configuration and diagnostics partition",
    0x14: "Hidden DOS 16-bit FAT < 32 MB, or AST DOS",
    0x16: "Hidden DOS 16-bit FAT >= 32M",
    0x17: "Hidden IFS (e.g., HPFS)",
    0x18: "AST SmartSleep Partition",
    0x1b: "Hidden WIN95 OSR2 FAT32",
    0x1c: "Hidden WIN95 OSR2 FAT32, LBA-mapped",
    0x1e: "Hidden WIN95 16-bit FAT, LBA-mapped",
    0x24: "NEC DOS 3.x",
    0x27: "Windows RE, or PQservice/MirOS/RouterBoot",
    0x2a: "AtheOS File System (AFS)",
    0x2b: "SyllableSecure (SylStor)",
    0x32: "NOS",
    0x35: "JFS on OS/2 or eCS ",
    0x38: "THEOS ver 3.2 2gb partition",
    0x39: "Plan 9 partition",
    0x39: "THEOS ver 4 spanned partition",
    0x3a: "THEOS ver 4 4gb partition",
    0x3b: "THEOS ver 4 extended partition",
    0x3c: "PartitionMagic recovery partition",
    0x3d: "Hidden NetWare",
    0x40: "Venix 80286, or PICK",
    0x41: "Linux/MINIX-DRDOS/Personal RISC Boot/PPC PReP",
    0x42: "Windows 2000 dynamic/Linux swap+DRDOS/SFS",
    0x43: "Linux native+DRDOS",
    0x44: "GoBack partition",
    0x45: "Boot-US boot manager/Priam/EUMEL/Elan",
    0x46: "EUMEL/Elan",
    0x47: "EUMEL/Elan",
    0x48: "EUMEL/Elan",
    0x4a: "ALFS/THIN/AdaOS Aquila",
    0x4c: "Oberon partition",
    0x4d: "QNX4.x",
    0x4e: "QNX4.x 2nd part",
    0x4f: "QNX4.x 3rd part/Oberon partition",
    0x50: "OnTrack Disk Manager/Lynx/Native Oberon",
    0x51: "OnTrack Disk Manager RW (DM6 Aux1)/Novell",
    0x52: "CP/M, or Microport SysV/AT",
    0x53: "Disk Manager 6.0 Aux3",
    0x54: "Disk Manager 6.0 Dynamic Drive Overlay (DDO)",
    0x55: "EZ-Drive",
    0x56: "Golden Bow VFeature, or DM EZ-BIOS, or AT&T MS-DOS 3.x",
    0x57: "DrivePro, or VNDI Partition",
    0x5c: "Priam EDisk",
    0x61: "SpeedStor",
    0x63: "Unix System V (SCO, ISC Unix, UnixWare, ...), Mach, GNU Hurd",
    0x64: "PC-ARMOUR, or Novell Netware 286, 2.xx",
    0x65: "Novell Netware 386, 3.xx or 4.xx",
    0x66: "Novell Netware SMS Partition",
    0x67: "Novell",
    0x68: "Novell",
    0x69: "Novell Netware 5+, Novell Netware NSS Partition",
    0x70: "DiskSecure Multi-Boot",
    0x72: "V7/x86",
    0x74: "Scramdisk partition",
    0x75: "IBM PC/IX",
    0x77: "M2FS/M2CS/VNDI partition",
    0x78: "XOSL FS",
    0x80: "MINIX until 1.4a",
    0x81: "MINIX since 1.4b, early Linux, Mitac disk manager",
    0x82: "Linux swap, or Solaris x86, or Prime",
    0x83: "Linux native",
    0x84: "OS/2 hidden C: drive, or Hibernation partition",
    0x85: "Linux extended partition",
    0x86: "Old Linux RAID partition superblock, or FAT16 volume set",
    0x87: "NTFS volume set",
    0x88: "Linux plaintext partition table",
    0x8a: "AiR-BOOT Linux Kernel",
    0x8b: "Legacy Fault Tolerant FAT32 volume",
    0x8c: "Legacy Fault Tolerant FAT32 volume using BIOS extd INT 13h",
    0x8d: "Free FDISK 0.96+ hidden Primary DOS FAT12 partitition",
    0x8e: "Linux Logical Volume Manager partition",
    0x90: "Free FDISK 0.96+ hidden Primary DOS FAT16 partitition",
    0x91: "Free FDISK 0.96+ hidden DOS extended partitition",
    0x92: "Free FDISK 0.96+ hidden Primary DOS large FAT16 partitition",
    0x93: "Hidden Linux native partition, or Amoeba",
    0x94: "Amoeba bad block table",
    0x95: "MIT EXOPC native partitions",
    0x96: "CHRP ISO-9660 filesystem",
    0x97: "Free FDISK 0.96+ hidden Primary DOS FAT32 partitition",
    0x98: "Free FDISK 0.96+ LBA/Datalight ROM-DOS Super-Boot",
    0x99: "DCE376 logical drive",
    0x9a: "Free FDISK 0.96+ hidden Primary DOS FAT16 partitition (LBA)",
    0x9b: "Free FDISK 0.96+ hidden DOS extended partitition (LBA)",
    0x9e: "ForthOS partition",
    0x9f: "BSD/OS",
    0xa0: "Laptop hibernation partition",
    0xa1: "Laptop hibernation partition/HP SpeedStor",
    0xa3: "HP Volume Expansion (SpeedStor variant)",
    0xa4: "HP Volume Expansion (SpeedStor variant)",
    0xa5: "BSD/386, 386BSD, NetBSD, FreeBSD",
    0xa6: "OpenBSD, or HP Volume Expansion (SpeedStor variant)",
    0xa7: "NeXTStep",
    0xa8: "Mac OS-X",
    0xa9: "NetBSD",
    0xaa: "Olivetti Fat 12 1.44MB Service Partition",
    0xab: "Mac OS-X Boot partition, or GO! partition",
    0xae: "ShagOS filesystem",
    0xaf: "ShagOS swap partition, or MacOS X HFS",
    0xb0: "BootStar Dummy",
    0xb1: "HP SpeedStor/QNX Neutrino Power-Safe",
    0xb2: "QNX Neutrino Power-Safe filesystem",
    0xb3: "HP SpeedStor/QNX Neutrino Power-Safe",
    0xb4: "HP Volume Expansion (SpeedStor variant)",
    0xb6: "HP SpeedStor/Corrupted Windows NT mirror set FAT16",
    0xb7: "Corrupted Windows NT mirror set (master), NTFS file system",
    0xb7: "BSDI BSD/386 filesystem",
    0xb8: "BSDI BSD/386 swap partition",
    0xbb: "Boot Wizard hidden",
    0xbc: "Acronis backup partition",
    0xbe: "Solaris 8 boot partition",
    0xbf: "New Solaris x86 partition",
    0xc0: "CTOS, or REAL/32, or NTFT, or DR-DOS/Novell DOS",
    0xc1: "DRDOS/secured (FAT-12)",
    0xc2: "Hidden Linux",
    0xc3: "Hidden Linux swap",
    0xc4: "DRDOS/secured (FAT-16, &lt; 32M)",
    0xc5: "DRDOS/secured (extended)",
    0xc6: "DRDOS/secured (FAT-16, &gt;= 32M) or Windows NT corrupted FAT16",
    0xc7: "Windows NT corrupted NTFS volume/stripe set, or Syrinx boot",
    0xc8: "Reserved for DR-DOS 8.0+",
    0xc9: "Reserved for DR-DOS 8.0+",
    0xca: "Reserved for DR-DOS 8.0+",
    0xcb: "DR-DOS 7.04+ secured FAT32 (CHS)/",
    0xcc: "DR-DOS 7.04+ secured FAT32 (LBA)/",
    0xcd: "CTOS Memdump? ",
    0xce: "DR-DOS 7.04+ FAT16X (LBA)/",
    0xcf: "DR-DOS 7.04+ secured EXT DOS (LBA)/",
    0xd0: "REAL/32 secure big partition, or Multiuser DOS",
    0xd1: "Old Multiuser DOS secured FAT12",
    0xd4: "Old Multiuser DOS secured FAT16 &lt;32M",
    0xd5: "Old Multiuser DOS secured extended partition",
    0xd6: "Old Multiuser DOS secured FAT16 &gt;=32M",
    0xd8: "CP/M-86",
    0xda: "Non-FS Data, or Powercopy Backup",
    0xdb: "DR CP/M, Concurrent CP/M, Concurrent DOS, CTOS, KDG Telemetry",
    0xdd: "Hidden CTOS Memdump?",
    0xde: "Dell PowerEdge Server utilities (FAT fs)",
    0xdf: "DG/UX or BootIt EMBRM",
    0xe0: "STMicroelectronics AVFS",
    0xe1: "DOS access or SpeedStor 12-bit FAT extended partition",
    0xe3: "DOS R/O or SpeedStor",
    0xe4: "SpeedStor 16-bit FAT extended partition &lt; 1024 cyl.",
    0xe5: "Tandy MSDOS with logically sectored FAT",
    0xe6: "Storage Dimensions SpeedStor",
    0xe8: "LUKS",
    0xeb: "BeOS BFS",
    0xec: "SkyOS SkyFS",
    0xee: "Indication that this legacy MBR is followed by an EFI header",
    0xef: "Partition that contains an EFI file system",
    0xf0: "Linux/PA-RISC boot loader",
    0xf1: "Storage Dimensions SpeedStor",
    0xf2: "DOS 3.3+ secondary partition",
    0xf4: "SpeedStor, or Prologue single-volume partition",
    0xf5: "Prologue multi-volume partition",
    0xf6: "Storage Dimensions SpeedStor",
    0xf7: "DDRdrive Solid State File System",
    0xf9: "pCache",
    0xfa: "Bochs",
    0xfb: "VMware File System partition",
    0xfc: "VMware Swap partition",
    0xfd: "Linux raid partition autodetect",
    0xfe: "SpeedStor/LANstep/IBM PS/2 IML/Windows NT/Linux LVM",
    0xff: "Xenix Bad Block Table",
}

def human_size(bytes):
    value = bytes
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

class BlockDevice(object):
    def __init__(self, name, size, type=0, desc=None):
        self._name = name
        self._size = size
        self._type = type
        self._desc = desc

    @property
    def name(self):
        return self._name

    @property
    def size(self):
        return self._size

    @property
    def humanSize(self):
        return human_size(self._size)

    @property
    def nodeName(self):
        return "/dev/%s" % self.name

    @property
    def conciseString(self):
        return self.deviceName

class Disk(BlockDevice):
    @property
    def humanLabel(self):
        return "%s (Disk, %s)" % (self.name, self.humanSize)

class Partition(BlockDevice):
    def __init__(self, name, size, type=0, desc=None):
        BlockDevice.__init__(self, name, size)
        self._type = type
        self._desc = desc

    @property
    def type(self):
        return self._type

    @property
    def desc(self):
        return self._desc
    
    @property
    def typeString(self):
        if self.type in partition_types:
            return partition_types[self.type]
        else:
            return "Unknown type %02x" % self.type
            
    @property
    def humanLabel(self):
        return "%s (%s, %s)" % (self.name, self.desc,
            self.humanSize)

    @property
    def nodeName(self):
        return "/dev/%s" % self.name

    @property
    def conciseString(self):
        return self.deviceName

class Endpoint(object):
    @property
    def name(self):
        return self._name
    
    @property
    def hasDevice(self):
        return False
            
    @property
    def hasImageFile(self):
        return False

    @property
    def hasServerName(self):
        return False

    @property
    def hasServerUser(self):
        return False

    @property
    def hasServerPassword(self):
        return False

    @property
    def hasShareShare(self):
        return False

    @property
    def hasServerPath(self):
        return False

    # override to return true if the device node is mounted
    @property
    def inUse(self):
        return False

    # override to return True if the other endpoint cannot be written to
    # without corrupting this one, or vice versa
    def overlaps(self, other):
        return True

def IsDeviceOverlap(device1, device2):
    common_len = min(len(device1), len(device2))
    device1 = device1[:common_len]
    device2 = device2[:common_len]
    return device1 == device2

class LocalDevice(Endpoint):
    def __init__(self, device=None):
        self._device = device
    
    @property
    def name(self):
        return "Local disk or partition"

    @property
    def hasDevice(self):
        return True
    
    @property
    def device(self):
        return self._device
        
    @device.setter
    def device(self, device):
        self._device = device

    @property
    def description(self):
        return self._device.conciseString
    
    @property
    def inUse(self):
        myDevice = self._device.nodeName
        
        with open("/etc/mtab") as mtab:
            for line in mtab:
                match = re.match(r'(\S+) (\S+) .*', line)
                
                if not match:
                    raise StandardError('Unknown line format in ' +
                        '/etc/mtab: %s' % line)
                
                mountedDevice = match.group(1)
                if IsDeviceOverlap(myDevice, mountedDevice):
                    return ('%s is busy:\n\n%s is mounted on %s' %
                        (myDevice, mountedDevice, match.group(2)))
        
        with open("/proc/swaps") as swaps:
            swaps.readline() # discard header
            
            for line in swaps:
                match = re.match(r'(\S+).*', line)
                
                if not match:
                    raise StandardError('Unknown line format in ' +
                        '/proc/swaps: %s' % line)
                
                mountedDevice = match.group(1)
                if IsDeviceOverlap(myDevice, mountedDevice):
                    return ('%s is busy:\n\n%s is an active swap partition' %
                        (myDevice, mountedDevice))
                
        return False

    def openInput(self):
        return open(self._device.nodeName, "r")

    def openOutput(self):
        return open(self._device.nodeName, "w")
    
    def overlaps(self, other):
        return other.hasDevice and IsDeviceOverlap(self.device.nodeName,
            other.device.nodeName)

class ImageFile(Endpoint):
    @property
    def name(self):
        return "Image file"

    @property
    def hasImageFile(self):
        return True

    @property
    def imageFile(self):
        return self._imageFile

    @imageFile.setter
    def imageFile(self, imageFile):
        self._imageFile = imageFile

    @property    
    def description(self):
        return self._imageFile

class GenericServer(Endpoint):
    @property
    def hasServerName(self):
        return True

    @property
    def hasServerUser(self):
        return True

    @property
    def hasServerPassword(self):
        return True

    @property
    def hasServerPath(self):
        return True

class FtpServer(GenericServer):
    @property
    def name(self):
        return "FTP server"

class SshServer(GenericServer):
    @property
    def name(self):
        return "SSH server"

class SmbServer(GenericServer):
    @property
    def name(self):
        return "Windows or Samba server"

class MulticastNetwork(Endpoint):
    @property
    def name(self):
        return "Multicast network"

sourcePoints = [LocalDevice(), ImageFile(), FtpServer(), SshServer(),
    SmbServer(), MulticastNetwork()]

destPoints = [LocalDevice(), ImageFile(), FtpServer(), SshServer(),
    SmbServer(), MulticastNetwork()]

devices = list()

class InitialSelectionEvent(wx.PyCommandEvent):
    def GetSelection(self):
        return 0

class EndpointSetter(object):
    def __init__(self, frame, items, column, isDestination):
        self.endpoints = items
        
        self.typeBox = frame.addChoiceControl('Type',
            [ep.name for ep in items], (1, column))
        
        self.devBox = frame.addChoiceControl('Device', [], (2, column))

        if isDestination:
            flpStyle = wx.FLP_SAVE | wx.FLP_OVERWRITE_PROMPT
        else:
            flpStyle = wx.FLP_OPEN | wx.FLP_FILE_MUST_EXIST
        
        self.imageFileBox = frame.addWithLabel('Image file',
            wx.FilePickerCtrl(frame,
                wildcard="Image files (*.img)|*.img|All files|*",
                style=flpStyle), (3, column))
                
        self.typeBox.Bind(wx.EVT_CHOICE, self.OnTypeChange)
        self.OnTypeChange()

        self.devBox.Bind(wx.EVT_CHOICE, self.OnDeviceChange)
        self.Refresh()

        self.imageFileBox.Bind(wx.EVT_FILEPICKER_CHANGED,
            self.OnImageFileChange)
        if self.endpoint.hasImageFile:
            self.OnImageFileChange()
    
    def OnTypeChange(self, event=None):
        self.endpoint = self.endpoints[self.typeBox.Selection]
        self.devBox.Enable(self.endpoint.hasDevice)
        self.imageFileBox.Enable(self.endpoint.hasImageFile)

    def OnDeviceChange(self, event=None):
        if self.devBox.Selection >= 0:
            self.endpoint.device = devices[self.devBox.Selection]

    def OnImageFileChange(self, event=None):
        self.endpoint.imageFile = self.imageFileBox.Path
        
    @property
    def description(self):
        return self.endpoint.description
        
    @property
    def inUse(self):
        return self.endpoint.inUse
        
    def Refresh(self):
        oldLabel = self.devBox.StringSelection
        self.devBox.Items = [dev.humanLabel for dev in devices]
        found = False

        for i, label in enumerate(self.devBox.Items):
            if label == oldLabel:
                self.devBox.Selection = i
                found = True
                break
        
        if not found:
            self.devBox.Selection = 0
        
        if self.endpoint.hasDevice:
            self.OnDeviceChange()

class MainWindow(wx.Frame):
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,id,title)
        self.parent = parent
        self.readPartitions()
        self.initialize()

    def readPartitions(self):
        global devices
        devices = list()
        sys_block = "/sys/block/"
        
        for devname in os.listdir(sys_block):
            # ignore loop and ramdisk devices, not very interesting to us
            if (re.match(r"(loop|ram)\d+", devname)):
                continue
            
            with open("%s/%s/size" % (sys_block, devname)) as size_file:
                disk_size = int(size_file.readline()) * 512
                
            devices.append(Disk(devname, disk_size))
            
            sfdisk = subprocess.Popen(['sfdisk', '-l', '-uS', '/dev/' + devname],
                stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            
            if not sfdisk:
                raise StandardError('sfdisk failed' % returnCode)
                
            sfout = sfdisk.stdout
            
            line = sfout.readline()
            if line != '\n':
                raise StandardError('Unknown output from sfdisk: %s' % line)
                
            line = sfout.readline()
            if not re.match(r'Disk /dev/' + devname + ': .*', line):
                raise StandardError('Unknown output from sfdisk: %s' % line)

            line = sfout.readline()
            if not re.match(r'Units = sectors of 512 bytes, counting from 0.*', line):
                raise StandardError('Unknown output from sfdisk: %s' % line)

            line = sfout.readline()
            if line != '\n':
                raise StandardError('Unknown output from sfdisk: %s' % line)
                
            #    Device Boot    Start       End   #sectors  Id  System
            line = sfout.readline()
            if not re.match(r'\s+Device\s+Boot\s+Start\s+End\s+#sectors' +
                '\s+Id\s+System', line):
                raise StandardError('Unknown output from sfdisk: %s' % line)

            for line in sfout.readlines():
                # /dev/sda1   *      2048 607444991  607442944  83  Linux
                found = re.match('/dev/(' + devname + r'\d+)' +
                    r'\s+(\*)?\s+\d+\s+\S+\s+(\d+)\s+(\S+)\s+(.+)', line)
                
                if not found:
                    raise StandardError('Unknown line format from ' +
                        'sfdisk for %s: %s' % (devname, line))
                
                if found.group(4) == '0':
                    # empty partition table entry
                    continue
                    
                devices.append(Partition(found.group(1),
                    int(found.group(3)) * 512,
                    int(found.group(4), 16), found.group(5)))
            
            returnCode = sfdisk.wait()
            if returnCode != 0:
                raise StandardError('sfdisk returned %d' % returnCode)
                
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
        
    def addSourceOrDestOptions(self, items, column, isDestination):
        return EndpointSetter(self, items, column, isDestination)

    def initialize(self):
        self.colSizer = wx.BoxSizer(orient=wx.VERTICAL)
        borderWidth = 6
        colFlags = wx.SizerFlags(0).Border(wx.ALL, borderWidth * 2).Expand()
        
        self.presetList = wx.Choice(self, choices=('Clone disk to disk',
            'Backup disk to network', 'Restore disk from network',
            'Backup partition to network', 'Restore partition from network',
            'Wipe disk'))
        self.colSizer.AddF(self.presetList, colFlags)
        colFlags.Border(wx.BOTTOM | wx.LEFT | wx.RIGHT, borderWidth * 2)
        
        self.gridSizer = wx.GridBagSizer(borderWidth, borderWidth)
        self.colSizer.AddF(self.gridSizer, colFlags.Proportion(1))
        
        self.gridSizer.Add(wx.StaticText(self, label='Source'), (0,1),
            flag=wx.ALIGN_CENTER)
        self.gridSizer.Add(wx.StaticText(self, label='Method'), (0,3),
            flag=wx.ALIGN_CENTER)
        self.gridSizer.Add(wx.StaticText(self, label='Destination'), (0,5),
            flag=wx.ALIGN_CENTER)

        self.source = self.addSourceOrDestOptions(sourcePoints, 0, False)
        self.dest = self.addSourceOrDestOptions(destPoints, 4, True)

        method_choices = ('Raw copy', 'Smart partition copy',
            'MBR copy', 'Rescue copy')

        self.methodList = self.addChoiceControl('Method',
            method_choices, (1,2))
            
        compression_choices = ('None', 'LZOP (fast)', 'Gzip (slow)',
            'Bzip2 (really slow)')
            
        self.compressList = self.addChoiceControl('Compression (out)',
            compression_choices, (2,2))

        errors_choices = ('Log and Skip', 'Log and Bisect',
            'Rewrite bad sectors')
            
        self.errorsList = self.addChoiceControl('Error recovery',
            errors_choices, (3,2))
        
        self.buttonSizer = wx.StdDialogButtonSizer()
        self.colSizer.AddF(self.buttonSizer, colFlags.Proportion(0))
        
        self.startButton = wx.lib.buttons.ThemedGenBitmapTextButton(self,
            id=wx.ID_OK, label="Copy",
            bitmap=wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_BUTTON))
        self.buttonSizer.Add(self.startButton)
        # self.buttonSizer.SetAffirmativeButton(self.startButton)
        self.startButton.Bind(wx.EVT_BUTTON, self.OnStartCopy)

        self.refreshButton = wx.Button(self, id=wx.ID_REFRESH)
        self.buttonSizer.Add(self.refreshButton)
        self.refreshButton.Bind(wx.EVT_BUTTON, self.OnRefresh)
        
        self.SetSizerAndFit(self.colSizer)
        self.OnRefresh()
        self.Show(True)
        
    def ShowMessage(self, msg, title, style):
        dlg = wx.lib.agw.genericmessagedialog.GenericMessageDialog(self,
            msg, "Concur: %s" % title, style)
        result = dlg.ShowModal()
        print "result = %s" % result
        dlg.Destroy()
        return result
        
    def OnRefresh(self, event=None):
        self.readPartitions()
        self.source.Refresh()
        self.dest.Refresh()
   
    def OnStartCopy(self, event):
        if (self.source.endpoint.overlaps(self.dest.endpoint)):
            self.ShowMessage("The source and destination overlap.\n" +
                "It is forbidden to destroy the source copy by " +
                "overwriting it.",
                "Error: Source and destination overlap",
                wx.ICON_ERROR | wx.OK)
            return
        
        sourceBusy = self.source.inUse
        if sourceBusy:
            if self.ShowMessage(("%s.\n\nYour copy may be corrupted by " +
                "filesystem activity.\nDo you want to copy anyway?") %
                sourceBusy, "Warning: Source device is in use",
                wx.ICON_WARNING | wx.YES_NO) != wx.ID_YES:
                return

        destBusy = self.dest.inUse
        if destBusy:
            self.ShowMessage(("%s.\n\nOverwriting a mounted filesystem " +
                "is forbidden\nto prevent operating system crashes and\n" +
                "potential serious data loss.") % destBusy,
                "Error: Destination device is in use",
                wx.ICON_ERROR | wx.OK)
            return

        sda = Disk("sda", 0)
        if self.dest.endpoint.overlaps(LocalDevice(sda)):
            self.ShowMessage("It is forbidden to overwrite /dev/sda\n" +
                "to prevent major accidental data loss.",
                "Error: Destination device is /dev/sda",
                wx.ICON_ERROR | wx.OK)
            return

        prog = wx.ProgressDialog("Copying",
            "Copying from %s to %s" % (self.source.description,
                self.dest.description),
            parent=self, style=wx.PD_CAN_ABORT | wx.PD_ESTIMATED_TIME)
        self.source.prepareSource()
        self.dest.prepareDest()
        self.Bind(wx.EVT_IDLE, self.OnIdleBackgroundCopy)
    
    def OnIdleBackgroundCopy(self, event):
        pass

if __name__ == "__main__":
    app = wx.App()
    frame = MainWindow(None, -1, 'Concur')
    app.MainLoop()
