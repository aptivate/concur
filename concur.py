#!/usr/bin/python
# -*- coding: utf-8 -*-

import fcntl
import inspect
import keyword
import lzo
import os
import operator
import optparse
import re
import stat
import subprocess
import sys

from collections import namedtuple

try:
    import wx
except ImportError:
    raise ImportError, "The wxPython module is required to run this program"

from wx.lib.agw.genericmessagedialog import GenericMessageDialog as MessageDialog

# http://www.win.tue.nl/~aeb/partitions/partition_types-1.html

"""Mapping of partition type codes from the partition table (downloaded
from http://www.win.tue.nl/~aeb/partitions/partition_types-1.html) to
descriptive names, used to help identify partitions in the drop-down 
lists, somewhat reformatted to reduce the width of the drop-down list
box."""

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

def extended_tuple(typename, baseclass, additional_field_names, verbose=False):
    """Returns a new subclass of tuple with named fields.

    >>> Point = namedtuple('Point', 'x y')
    >>> RoundedPoint = namedtuple('RoundedPoint', Point, 'radius')
    """

    # Parse and validate the field names.  Validation serves two purposes,
    # generating informative error messages and preventing template injection attacks.
    if isinstance(additional_field_names, basestring):
        additional_field_names = additional_field_names.replace(',', ' ').split() # names separated by whitespace and/or commas
    additional_field_names = tuple(map(str, additional_field_names))
    for name in (typename,) + additional_field_names:
        if not all(c.isalnum() or c=='_' for c in name):
            raise ValueError('Type names and field names can only contain alphanumeric characters and underscores: %r' % name)
        if keyword.iskeyword(name):
            raise ValueError('Type names and field names cannot be a keyword: %r' % name)
        if name[0].isdigit():
            raise ValueError('Type names and field names cannot start with a number: %r' % name)
    seen_names = set()
    for name in additional_field_names:
        if name.startswith('_'):
            raise ValueError('Field names cannot start with an underscore: %r' % name)
        if name in seen_names:
            raise ValueError('Encountered duplicate field name: %r' % name)
        seen_names.add(name)

    # Create and fill-in the class template
    numfields = len(baseclass._fields) + len(additional_field_names)
    argtxt = repr(baseclass._fields + additional_field_names).replace("'",
        "")[1:-1]   # tuple repr without parens or quotes
    reprtxt = ', '.join('%s=%%r' % name for name in baseclass._fields +
        additional_field_names)
    dicttxt = ', '.join('%r: t[%d]' % (name, pos) for pos, name in
        enumerate(baseclass._fields + additional_field_names))
    baseclass_name = baseclass.__name__

    template = '''
import operator

class %(typename)s(%(baseclass_name)s):
        '%(typename)s(%(argtxt)s)' \n
        __slots__ = () \n
        _fields = %(additional_field_names)r \n
        def __new__(_cls, %(argtxt)s):
            return _tuple.__new__(_cls, (%(argtxt)s)) \n
        @classmethod
        def _make(cls, iterable, new=tuple.__new__, len=len):
            'Make a new %(typename)s object from a sequence or iterable'
            result = new(cls, iterable)
            if len(result) != %(numfields)d:
                raise TypeError('Expected %(numfields)d arguments, got %%d' %% len(result))
            return result \n
        def __repr__(self):
            return '%(typename)s(%(reprtxt)s)' %% self \n
        def _asdict(t):
            'Return a new dict which maps field names to their values'
            return {%(dicttxt)s} \n
        def _replace(_self, **kwds):
            'Return a new %(typename)s object replacing specified fields with new values'
            result = _self._make(map(kwds.pop, %(additional_field_names)r, _self))
            if kwds:
                raise ValueError('Got unexpected field names: %%r' %% kwds.keys())
            return result \n
        def __getnewargs__(self):
            return tuple(self) \n\n''' % locals()
    for i, name in enumerate(additional_field_names):
        template += '        %s = _property(operator.itemgetter(%d))\n' % (name, i)
    if verbose:
        print template

    # Execute the template string in a temporary namespace and
    # support tracing utilities by setting a value for frame.f_globals['__name__']
    namespace = dict(__name__='namedtuple_%s' % typename,
        _property=property, _tuple=tuple)
    namespace[baseclass_name] = baseclass

    try:
        exec template in namespace
    except SyntaxError, e:
        raise SyntaxError("%s:\n%s" % (e, template))

    result = namespace[typename]

    # For pickling to work, the __module__ variable needs to be set to the frame
    # where the named tuple is created.  Bypass this step in enviroments where
    # sys._getframe is not defined (Jython for example).
    if hasattr(sys, '_getframe'):
        result.__module__ = sys._getframe(1).f_globals.get('__name__', '__main__')

    return result

def human_readable_size(bytes):
    """Utility function to convert a size in bytes into a human-readable
    formatted number for display. Uses the "SI" definition of a megabyte
    and a gigabyte, as disk manufacturers do, rather than the binary-based
    mebibyte and gigibyte favoured by purists and RAM modules."""

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

class BlockDevice(namedtuple('BlockDeviceTuple', 'name size')):
    """Represents a generic block device, i.e. something which is
    represented by a device node under /dev, and can store a fixed
    number of bytes.
    
    Constructor arguments: name is the device name without /dev
    (e.g. sda1), size is the size in bytes."""
    
    @property
    def human_readable_size(self):
        """Returns the human-readable version of the block device size.
        Read-only property."""
        return human_readable_size(self.size)

    @property
    def device_node(self):
        """Returns the device name (in the filesystem), used for permission
        checks before imaging starts."""
        return "/dev/%s" % self.name

    @property
    def very_short_desc(self):
        """Returns a short string describing the block device, in this case
        just its device node name. This is used as the description property
        of a LocalDevice endpoint that wraps this block device."""
        return self.device_node

class Disk(BlockDevice):
    """Represents an entire disk, a BlockDevice which can contain a
    partition table."""
    
    @property
    def listbox_label(self):
        """listbox_label is the name shown in the drop-down list of block 
        devices (disks and partitions)."""
        return "%s (Disk, %s)" % (self.name, self.human_readable_size)

class PermissionDeniedDisk(Disk):
    """Represents a disk that we don't have permission to open, so we
    can't find out much about the sizes or types of the partitions on
    it. 
    
    We add this to the device list instead of a Disk to indicate to the
    user that they won't be able to read or write it unless they fix
    the permissions issue, for example by running concur as root or
    giving themselves access to the device node under /dev.
    
    Shows up as something like "/dev/sda (permission denied, 120 GB)"
    in the device list."""

    @property
    def listbox_label(self):
        """listbox_label is the name shown in the drop-down list of
        block devices (disks and partitions). PermissionDeniedDisk
        devices show up as something like "/dev/sda (permission denied,
        120 GB)"."""
        return "%s (permission denied, %s)" % (self.name,
            self.human_readable_size)

class Partition(extended_tuple('PartitionTuple', BlockDevice,
    'type_code desc')):
    """Represents an individual partition, a Block Device that has a
    partition type, mainly so that we display that partition type in
    the drop-down device list. Shows up as something like
    "/dev/sda1 (NTFS, 119 GB)" in the device list.
    
    Constructor arguments: name and size are passed directly to
    BlockDevice, type is the partition type code, and desc is the 
    descriptive version of the partition type code, which can be
    looked up from the partition_types, but currently the caller is
    expected to do this for us.
    """

    @property
    def listbox_label(self):
        """Returns the human-readable description of the partition,
        for the drop-down list box. Read-only."""
        return "%s (%s, %s)" % (self.name, self.desc,
            self.human_readable_size)

"""Represents a partition of unknown size, usually because the disk
that it's stored on is not readable."""
class UnknownPartition(BlockDevice):
    @property
    def listbox_label(self):
        return "%s (unknown type, %s)" % (self.name, self.human_readable_size)

"""Represents a place where image data can be stored or retrieved from.
Endpoints are very generic, including network shares, network multicasting,
block devices and files. Specific endpoint classes derive from Endpoint.
These classes are used to represent the options in the Source and
Destination lists, and tell the GUI whether to display or hide certain
options depending on the nature of the endpoint, such as whether to 
prompt the user for a user name and password when using this endpoint."""
class Endpoint(object):
    @property
    def name(self):
        return self._name
    
    @property
    def HasDevice(self):
        return False
            
    @property
    def HasImageFile(self):
        return False

    @property
    def HasServerName(self):
        return False

    @property
    def HasServerUser(self):
        return False

    @property
    def HasServerPassword(self):
        return False

    @property
    def HasShareShare(self):
        return False

    @property
    def HasServerPath(self):
        return False

    # override to return true if the device node is mounted
    @property
    def inUse(self):
        return False

    # override to return True if the other endpoint cannot be written to
    # without corrupting this one, or vice versa
    def overlaps(self, other):
        if self.HasDevice:
            myDevice = self.DeviceNode.device_node
        elif self.HasImageFile:
            myDevice = self.imageFileDevice
        else:
            return False # we don't need a device, so can't conflict

        if other.HasDevice:
            return IsDeviceOverlap(myDevice, other.DeviceNode.device_node)
        elif other.HasImageFile:
            return IsDeviceOverlap(myDevice, other.imageFileDevice)
        else:
            return False # other doesn't need a device, so can't conflict
    
    def _SetInput(self, handle):
        self._isOutput = False
        fcntl.lockf(handle, fcntl.LOCK_SH)
    
    def _SetOutput(self, handle):
        self._isOutput = True
        fcntl.lockf(handle, fcntl.LOCK_EX)
    
    @property
    def IsOutput(self):
        return self._isOutput
    
    def Cancel(self):
        # nothing to do by default, but some subclasses override this
        pass
        
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
    def HasDevice(self):
        return True

    @property
    def DeviceNode(self):
        return self._device
        
    @DeviceNode.setter
    def DeviceNode(self, device):
        self._device = device

    @property
    def description(self):
        return self._device.very_short_desc

    @property
    def inUse(self):
        myDevice = self._device.device_node
        
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

    def OpenInput(self):
        handle = open(self._device.device_node, "rb")
        self._SetInput(handle)
        return handle
        # caller must close handle when done

    def OpenOutput(self):
        handle = open(self._device.device_node, "wb")
        self._SetOutput(handle)
        return handle
        # caller must close handle when done

    def overlaps(self, other):
        if other.HasDevice:
            return IsDeviceOverlap(self.DeviceNode.device_node,
                other.DeviceNode.device_node)
        elif other.HasImageFile:
            return IsDeviceOverlap(self.DeviceNode.device_node,
                other.imageFileDevice)
        
    @property
    def size(self):
        return self._device.size

    def Recognises(self, name, exists, statinfo):
        return exists and stat.S_ISBLK(statinfo.st_mode)

class BitBucket(LocalDevice):
    def __init__(self):
        LocalDevice.__init__(self, BlockDevice("/dev/zero", None))

    @property
    def name(self):
        return "Bit bucket (discard/zero)"

    def Recognises(self, name, exists, statinfo):
        return name == "/dev/null" or name == "bitbucket"

class ImageFile(Endpoint):
    def __init__(self):
        self._imageFile = None
        
    @property
    def name(self):
        return "Image file"

    @property
    def HasImageFile(self):
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
        
    @property
    def inUse(self):
        # openInput or openOutput will fail if the file is in use and
        # sharing the lock is not appropriate, so just return False here.
        return False

    def OpenInput(self):
        handle = open(self._imageFile, "rb")
        Endpoint._SetInput(self, handle)
        return handle
        # caller must free handle when done

    def OpenOutput(self):
        handle = open(self._imageFile, "wb")
        Endpoint._SetOutput(self, handle)
        return handle
        # caller must free handle when done
        
    @property
    def imageFileDevice(self):
        if self._imageFile is None:
            return None
            
        foundDevice = None
        foundMount = None
        
        with open("/etc/mtab") as mtab:
            for line in mtab:
                match = re.match(r'(\S+) (\S+) .*', line)
                
                if not match:
                    raise StandardError('Unknown line format in ' +
                        '/etc/mtab: %s' % line)
                
                thisDevice = match.group(1)
                thisMount = match.group(2)
                
                # find the most specific (longest) matching mount
                # print "test for overlap: %s and %s" % (thisMount, self._imageFile)
                if IsDeviceOverlap(thisMount, self._imageFile):
                    if foundMount is None or len(thisMount) > len(foundMount):
                        foundDevice = thisDevice
                        foundMount = thisMount

        return foundDevice
    
    def Cancel(self):
        # override to remove the destination file if the copy is cancelled
        if self.IsOutput:
            os.unlink(self._imageFile)

    def Recognises(self, name, exists, statinfo):
        return not exists or stat.S_ISREG(statinfo.st_mode)

class GenericServer(Endpoint):
    @property
    def HasServerName(self):
        return True

    @property
    def HasServerUser(self):
        return True

    @property
    def HasServerPassword(self):
        return True

    @property
    def HasServerPath(self):
        return True

class FtpServer(GenericServer):
    @property
    def name(self):
        return "FTP server"

    def Recognises(self, name, exists, statinfo):
        return name.startswith('ftp:')

class SshServer(GenericServer):
    @property
    def name(self):
        return "SSH server"

    def Recognises(self, name, exists, statinfo):
        return name.startswith('ssh:')

class SmbServer(GenericServer):
    @property
    def name(self):
        return "Windows or Samba server"

    def Recognises(self, name, exists, statinfo):
        return name.startswith('smb:')

class MulticastNetwork(Endpoint):
    @property
    def name(self):
        return "Multicast network"

    def Recognises(self, name, exists, statinfo):
        return name.startswith('multicast:')

sourcePoints = [LocalDevice(), ImageFile(), FtpServer(), SshServer(),
    SmbServer(), MulticastNetwork(), BitBucket()]

destPoints = [LocalDevice(), ImageFile(), FtpServer(), SshServer(),
    SmbServer(), MulticastNetwork(), BitBucket()]

devices = list()

class InitialSelectionEvent(wx.PyCommandEvent):
    def GetSelection(self):
        return 0

class EndpointUserInterface(object):
    def __init__(self, frame, items, column, isDestination):
        self.endpoints = items
        
        self.typeBox = frame.addChoiceControl('Type',
            [ep.name for ep in items], (1, column))
        
        self.devBox = frame.addChoiceControl('Device', [], (2, column))

        if isDestination:
            flpStyle = (wx.FLP_SAVE | wx.FLP_OVERWRITE_PROMPT |
                wx.PB_USE_TEXTCTRL)
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
        if self.endpoint.HasImageFile:
            self.OnImageFileChange()
    
    def OnTypeChange(self, event=None):
        self.endpoint = self.endpoints[self.typeBox.Selection]
        self.devBox.Enable(self.endpoint.HasDevice)
        self.imageFileBox.Enable(self.endpoint.HasImageFile)

    def OnDeviceChange(self, event=None):
        if self.devBox.Selection >= 0:
            self.endpoint.DeviceNode = devices[self.devBox.Selection]

    def OnImageFileChange(self, event=None):
        self.imageFileBox.Path = os.path.abspath(self.imageFileBox.Path)
        self.endpoint.imageFile = self.imageFileBox.Path

    @property
    def size(self):
        return self.endpoint.size
        
    @property
    def description(self):
        return self.endpoint.description
        
    @property
    def inUse(self):
        return self.endpoint.inUse
        
    def Refresh(self):
        oldLabel = self.devBox.StringSelection
        self.devBox.Items = [dev.listbox_label for dev in devices]
        found = False

        for i, label in enumerate(self.devBox.Items):
            if label == oldLabel:
                self.devBox.Selection = i
                found = True
                break
        
        if not found:
            self.devBox.Selection = 0
        
        if self.endpoint.HasDevice:
            self.OnDeviceChange()

    def OpenInput(self):
        return self.endpoint.OpenInput()

    def OpenOutput(self):
        return self.endpoint.OpenOutput()

    def _prepareError(self, frame, message):
        frame.ShowMessage(message, "Error: Required value missing",
            wx.ICON_ERROR | wx.OK)
        return False
    
    def Prepare(self, frame, whichEnd):
        ep = self.endpoint
        
        if ep.HasDevice:
            if ep.DeviceNode is None:
                return self._prepareError(frame,
                    "Please specify the %s device node" % whichEnd)
        
        if ep.HasImageFile:
            if ep.imageFile is None:
                return self._prepareError(frame,
                    "Please specify the %s image file name" % whichEnd)

            if ep.imageFileDevice is None:
                return self._prepareError(frame,
                    "Cannot identify mount device for image file %s" %
                        ep.imageFile)
        
        return True
    
    def Cancel(self):
        self.endpoint.Cancel()
        
    def SetByName(self, frame, descString):
        try:
            statinfo = os.stat(descString)
            exists = True
        except OSError as e:
            statinfo = None
            exists = False
        
        foundEndpointIndex = None
        
        # hope there isn't more than one match in the list!
        for i, ep in enumerate(self.endpoints):
            if ep.Recognises(descString, exists, statinfo):
                foundEndpointIndex = i
        
        if foundEndpointIndex is None:
            return self._prepareError(frame,
                "%s does not recognize target %s" % (self, descString))
        
        self.typeBox.Selection = foundEndpointIndex
        self.OnTypeChange()
        
        if self.endpoint.HasDevice:
            foundDeviceIndex = None
            
            for i, dev in enumerate(devices):
                devstats = os.stat(dev.device_node)
                if devstats.st_rdev == statinfo.st_rdev:
                    foundDeviceIndex = i

            if foundDeviceIndex is None:
                return self._prepareError(frame,
                    "%s is not one of the detected block devices %s" \
                    % (descString, repr(devices)))
            
            self.devBox.Selection = foundDeviceIndex
            self.OnDeviceChange()
        
        if self.endpoint.HasImageFile:
            self.imageFileBox.Path = os.path.abspath(descString)
            self.OnImageFileChange()
        
class MainWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Concur")
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
            
            devpath = "/dev/%s" % devname
            
            sfdisk = subprocess.Popen(['sfdisk', '-l', '-uS', devpath],
                stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
            
            if not sfdisk:
                raise StandardError('sfdisk failed' % returnCode)
                
            sfout = sfdisk.stdout
            line = sfout.readline()

            if line == ('%s: Permission denied\n' % devpath):
                devices.append(PermissionDeniedDisk(devname, disk_size))
                
                # alternative method, scan /sys/block/sda for subdirs
                # with partition information, doesn't require permissions
                for partname in os.listdir('%s/%s' % (sys_block, devname)):
                    sys_block_disk_part = '%s/%s/%s' % (sys_block,
                        devname, partname)
                    
                    if os.access('%s/partition' % sys_block_disk_part, os.F_OK):
                        with open("%s/size" % sys_block_disk_part) as size_file:
                            partition_size = int(size_file.readline()) * 512
                        devices.append(UnknownPartition(partname,
                            partition_size))
            else:
                devices.append(Disk(devname, disk_size))
            
                if line != '\n':
                    raise StandardError('Unknown output from sfdisk (1): %s' % line)
                    
                line = sfout.readline()
                if not re.match(r'Disk /dev/' + devname + ': .*', line):
                    raise StandardError('Unknown output from sfdisk (2): %s' % line)

                line = sfout.readline()
                
                if line == 'Warning: extended partition does not start at a cylinder boundary.\n':
                    line = sfout.readline()
                    if line == 'DOS and Linux will interpret the contents differently.\n':
                        line = sfout.readline()
                
                if not re.match(r'Units = sectors of 512 bytes, counting from 0.*', line):
                    raise StandardError('Unknown output from sfdisk (3): %s' % line)

                line = sfout.readline()
                if line != '\n':
                    raise StandardError('Unknown output from sfdisk (4): %s' % line)
                    
                #    Device Boot    Start       End   #sectors  Id  System
                line = sfout.readline()
                if not re.match(r'\s+Device\s+Boot\s+Start\s+End\s+#sectors' +
                    '\s+Id\s+System', line):
                    raise StandardError('Unknown output from sfdisk (5): %s' % line)

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
                
                sfout.close()
                
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
        return EndpointUserInterface(self, items, column, isDestination)

    def initialize(self):
        self.colSizer = wx.BoxSizer(orient=wx.VERTICAL)
        borderWidth = 6
        colFlags = wx.SizerFlags(0).Border(wx.ALL, borderWidth * 2).Expand()
        
        self.presetList = wx.Choice(self, choices=('Clone disk to disk',
            'Backup disk to network', 'Restore disk from network',
            'Backup partition to network', 'Restore partition from network',
            'Wipe disk', 'Read test', 'Compare contents'))
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
            'MBR copy', 'Rescue copy', 'Read test (read only)', 'Checksum',
            'Compare contents', 'Multicast entire disk',
            'Multicast blocks (experimental)')

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
        # print "result = %s" % result
        dlg.Destroy()
        return result
        
    def SetSourceByName(self, source):
        self.source.SetByName(source)

    def SetDestByName(self, dest):
        self.dest.SetByName(dest)
        
    def OnRefresh(self, event=None):
        self.readPartitions()
        self.source.Refresh()
        self.dest.Refresh()
        
    def Warn(self, message, title):
        if wx.GetApp()._options.ignore_warnings:
            return True
        
        return self.ShowMessage(message, title,
            wx.ICON_WARNING | wx.YES_NO) == wx.ID_YES
   
    def OnStartCopy(self, event=None):
        self.source.Prepare(self, "source")
        self.dest.Prepare(self, "destination")

        if (self.source.endpoint.overlaps(self.dest.endpoint)):
            self.ShowMessage("The source and destination overlap.\n" +
                "It is forbidden to destroy the source copy by " +
                "overwriting it.",
                "Error: Source and destination overlap",
                wx.ICON_ERROR | wx.OK)
            return
        
        sourceBusy = self.source.inUse
        if sourceBusy:
            if not self.Warn(("%s.\n\nYour copy may be corrupted by " +
                "filesystem activity.\nDo you want to copy anyway?") %
                sourceBusy, "Warning: Source device is in use"):
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

        self.input  = self.source.OpenInput()
        self.output = self.dest.OpenOutput()
        self.position = 0
        
        self.length = self.source.size
        if self.length is None:
            self.length = self.dest.size

        self.progress = wx.ProgressDialog("Copying",
            "Copying from %s to %s" % (self.source.description,
                self.dest.description),
            parent=self, style=wx.PD_CAN_ABORT | wx.PD_REMAINING_TIME)
        
        self.Bind(wx.EVT_IDLE, self.OnIdleBackgroundCopy)
    
    def OnIdleBackgroundCopy(self, event):
        bufsize = 128*1024
        buffer = self.input.read(bufsize)
        eof = (len(buffer) < bufsize)
        self.output.write(buffer)
        self.position += len(buffer)
        positionPercent = (self.position * 100) / self.length
        
        (cont, skip) = self.progress.Update(positionPercent)
        if not cont:
            eof = True
            self.source.Cancel()
            self.dest.Cancel()
            
        if eof:
            self.input.close()
            self.output.close()
            self.progress.Destroy()
            self.Unbind(wx.EVT_IDLE, handler=self.OnIdleBackgroundCopy)            
        else:
            event.RequestMore()
        
        wx.SafeYield(self.progress)
        
        if wx.GetApp()._options.exit_after:
            wx.Exit()

if __name__ == "__main__":
    app = wx.App()
    frame = MainWindow()

    parser = optparse.OptionParser()
    parser.add_option('-i', '--ignore-warnings', action="store_true",
        dest='ignore_warnings',
        help='Ignore (hide) warnings (e.g. device in use)')
    parser.add_option('-s', '--start-copy', action="store_true",
        dest='start_copy',
        help='Start copying automatically')
    parser.add_option('-x', '--exit-after', action="store_true",
        dest='exit_after',
        help='Exit after copying')
    (options, files) = parser.parse_args()
    
    if len(files) >= 1:
        frame.source.SetByName(frame, files.pop(0))

    if len(files) >= 1:
        frame.dest.SetByName(frame, files.pop(0))

    if len(files) >= 1:
        frame.ShowMessage(
            ("Unexpected command-line argument(s): %s." % repr(files)),
            "Error: Invalid command line",
            wx.ICON_ERROR | wx.OK)
        # Not safe to start automatically after a command-line error
        options.start_copy = False

    app._options = options
    
    if options.start_copy:
        frame.OnStartCopy(None)
    elif options.ignore_warnings:
        frame.ShowMessage(
            "Command-line option '--ignore-warnings' requires '--start-copy'",
            "Error: Invalid command line",
            wx.ICON_ERROR | wx.OK)
        sys.exit(2)
    elif options.exit_after:
        frame.ShowMessage(
            "Command-line option '--exit-after' requires '--start-copy'",
            "Error: Invalid command line",
            wx.ICON_ERROR | wx.OK)
        sys.exit(2)

    app.MainLoop()
