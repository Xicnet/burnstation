#!/usr/bin/python
# -*- coding: utf-8 -*-

import dbus
import dbus.glib
import sys
import os
import os.path
import string

class Drive:
    """ An Removable device abstraction """
    def __init__ (self, device, mp, name):
	self.device = device
	self.mountpoint = mp
	self.name = name

    def umount(self):
      return os.system("pumount %s" % self.device)

class DriveSelector:
    def __init__(self):

	label = "Select Import source"
	refresh = "Refresh"

        self.col1 = "Label"
        self.col2 = "Vendor"
        self.col3 = "Type"

        self.drives = []

	self.Refresh()

    def GetDir(self):
	i = self.list.GetFirstSelected()
	return Drive(str(self.mounts[i][0]), str(self.mounts[i][1]), str(self.mounts[i][2]))

    def Refresh(self, evt=None):
	# get a connection to the system bus
	bus = dbus.SystemBus ()

	# get a HAL object and an interface to HAL to make function calls
	hal_obj = bus.get_object ('org.freedesktop.Hal', '/org/freedesktop/Hal/Manager')
	hal = dbus.Interface (hal_obj, 'org.freedesktop.Hal.Manager')

	# find all devices that have the capability 'laptop_panel'
	udis = hal.FindDeviceByCapability ('volume')

	self.mounts = []
	for udi in udis:
	    # Get Volume Object for this mount point
            dev_obj = bus.get_object ('org.freedesktop.Hal', udi)

	    # get an interface to the device
            dev = dbus.Interface (dev_obj, 'org.freedesktop.Hal.Device')
        
	    # Get the parent device
	    parent_obj = bus.get_object ('org.freedesktop.Hal', dev.GetProperty("info.parent"))
            parent = dbus.Interface (parent_obj, 'org.freedesktop.Hal.Device')

            # Get removable and CDROM media only
            if parent.GetProperty ('storage.hotpluggable') or 'storage.cdrom' in parent.GetProperty('info.capabilities'):
		name = dev.GetProperty ('volume.label') or parent.GetProperty("info.product")
                device = dev.GetProperty ('block.device')
		try:
		    vendor = parent.GetProperty ('info.vendor')
		except:
		    vendor = parent.GetProperty('info.product')
		if 'storage.cdrom' in parent.GetProperty('info.capabilities'):
		    mtype = "CD-ROM"
		else:
		    mtype = "Pendrive"
		#if not dev.GetProperty('volume.is_mounted'):
		    #os.system("pmount -r %s %s" % (device, name.replace(" ", "_")))
		    #os.system("pmount-hal %s" % (udi))
                mountpoint = dev.GetProperty ('volume.mount_point')
                is_mounted = dev.GetProperty ('volume.is_mounted')
		self.drives.append( { 'name':str(name), 'vendor':str(vendor), 'mtype':str(mtype), 'mountpoint':mountpoint, 'is_mounted': is_mounted, 'device': device} )
		self.mounts.append((device, mountpoint, name))

#d = DriveSelector()
#print d.drives
