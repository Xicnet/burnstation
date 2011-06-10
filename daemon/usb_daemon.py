    
import dbus
import gobject
import os

class DeviceAddedListener:
     def __init__(self):
        self.bus = dbus.SystemBus()
        self.hal_manager_obj = self.bus.get_object(
                                              "org.freedesktop.Hal", 
                                              "/org/freedesktop/Hal/Manager")
        self.hal_manager = dbus.Interface(self.hal_manager_obj,
                                          "org.freedesktop.Hal.Manager")

        self.hal_manager.connect_to_signal("DeviceAdded", self._filter)


     def _filter(self, udi):
        device_obj = self.bus.get_object ("org.freedesktop.Hal", udi)
        device = dbus.Interface(device_obj, "org.freedesktop.Hal.Device")

        if device.QueryCapability("volume"):
            return self.do_something(device)


     def do_something(self, volume):
        device_file = volume.GetProperty("block.device")
        label = volume.GetProperty("volume.label")
        fstype = volume.GetProperty("volume.fstype")
        mounted = volume.GetProperty("volume.is_mounted")
        mount_point = volume.GetProperty("volume.mount_point")
        udi = volume.GetProperty("info.udi")
        print "UDI 2 = ", volume
        print udi

        if not volume.GetProperty('volume.is_mounted'):
            #os.system("pmount -r %s %s" % (device, name.replace(" ", "_")))
            os.system("pmount %s usburn" % (device_file))
            print "pmount %s usburn" % (device_file)
            mounted = volume.GetProperty('volume.is_mounted')
        mountpoint = volume.GetProperty ('volume.mount_point')
        print mountpoint


        try:
            size = volume.GetProperty("volume.size")
        except:
            size = 0

        print "New storage device detectec:"
        print "  device_file: %s" % device_file
        print "  label: %s" % label
        print "  fstype: %s" % fstype
        if mounted:
            print "  mount_point: %s" % mount_point
        else:
            print "  not mounted"
        print "  size: %s (%.2fGB)" % (size, float(size) / 1024**3)

if __name__ == '__main__':
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)
    loop = gobject.MainLoop()
    DeviceAddedListener()
    loop.run()

