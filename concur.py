#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

try:
    import wx
except ImportError:
    raise ImportError,"The wxPython module is required to run this program"

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

class Device(object):
    def __init__(self, name, size, type=0):
        self._name = name
        self._size = size
        self._type = type
        
    @property
    def name(self):
        return self._name

    @property
    def size(self):
        return self._size

    @property
    def type(self):
        return self._type
    
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
        
    def typeString(self):
        if self.type in partition_types:
            return partition_types[self.type]
        else:
            return "Unknown type 0x%02x" % self.type
            
    def humanLabel(self):
        return "%s (%s, %s)" % (self.name, self.typeString(),
            self.humanSize())

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
            [dev.humanLabel() for dev in self.devices],
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
        
        self.gridSizer.Add(wx.StaticText(self, label='Source'), (0,1), # (1,2),
            flag=wx.ALIGN_CENTER)
        self.gridSizer.Add(wx.StaticText(self, label='Method'), (0,3), # (1,2),
            flag=wx.ALIGN_CENTER)
        self.gridSizer.Add(wx.StaticText(self, label='Destination'), (0,5), # (1,2),
            flag=wx.ALIGN_CENTER)

        self.addSourceOrDestOptions(0, False)
        self.addSourceOrDestOptions(4, True)

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
        
        self.startButton = wx.Button(self, id=wx.ID_OK)
        self.buttonSizer.Add(self.startButton)
        self.buttonSizer.SetAffirmativeButton(self.startButton)
        
        self.SetSizerAndFit(self.colSizer)
        self.Show(True)

if __name__ == "__main__":
    app = wx.App()
    frame = MainWindow(None, -1, 'Concur')
    app.MainLoop()