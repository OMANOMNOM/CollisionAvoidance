#!/usr/bin/python3
from gi.repository import GLib
import bluetooth_utils
import bluetooth_constants
import dbus
import dbus.mainloop.glib
import sys
sys.path.insert(0, '.')
adapter_interface = None
mainloop = None
timer_id = None
# list of devices
devices = {}
managed_objects_found = 0

def get_known_devices(bus):
    global managed_objects_found
    object_manager = dbus.Interface(bus.get_object(bluetooth_constants.BLUEZ_SERVICE_NAME, "/"),
        bluetooth_constants.DBUS_OM_IFACE)
    managed_objects=object_manager.GetManagedObjects()

    for path, ifaces in managed_objects.items():
        for iface_name in ifaces:
            if iface_name == bluetooth_constants.DEVICE_INTERFACE:
                managed_objects_found += 1
                print("EXI path : ", path)
                device_properties = ifaces[bluetooth_constants.DEVICE_INTERFACE]
                devices[path] = device_properties
                if 'Address' in device_properties:
                    print("EXI bdaddr: ",
                        bluetooth_utils.dbus_to_python(device_properties['Address']))
                    print("------------------------------")

def properties_changed(interface, changed, invalidated, path):
    if interface != bluetooth_constants.DEVICE_INTERFACE:
        return
    if path in devices:
        devices[path] = dict(devices[path].items())
        devices[path].update(changed.items())
    else:
        devices[path] = changed
    
    dev = devices[path]
    print("CHG path :", path)
    if 'Address' in dev:
        print("CHG bdaddr: ",
    bluetooth_utils.dbus_to_python(dev['Address']))
    if 'Name' in dev:
        print("CHG name : ", bluetooth_utils.dbus_to_python(dev['Name']))
    if 'RSSI' in dev:
        print("CHG RSSI : ", bluetooth_utils.dbus_to_python(dev['RSSI']))
    print("------------------------------")

def list_devices_found():
    print("Full list of devices",len(devices),"discovered:")
    print("------------------------------")
    for path in devices:
        dev = devices[path]
        print(bluetooth_utils.dbus_to_python(dev['Address']))

# Called when we want to print interfaces (our callback)
# Only get details for new devices, not already known devices
def interfaces_added(path, interfaces):
    # interfaces is an array of dictionary entries
    if not bluetooth_constants.DEVICE_INTERFACE in interfaces:
        return
    device_properties = interfaces[bluetooth_constants.DEVICE_INTERFACE]
    if path not in devices:
        print("NEW path :", path)
    devices[path] = device_properties
    dev = devices[path]
    if 'Address' in dev:
        print("NEW bdaddr: ",
    bluetooth_utils.dbus_to_python(dev['Address']))
    if 'Name' in dev:
        print("NEW name : ",
    bluetooth_utils.dbus_to_python(dev['Name']))
    if 'RSSI' in dev:
        print("NEW RSSI : ",
    bluetooth_utils.dbus_to_python(dev['RSSI']))
        print("------------------------------")
    for i in dev:
        print(i)

def discover_devices(bus):
    global adapter_interface
    global mainloop
    global timer_id
    adapter_path = bluetooth_constants.BLUEZ_NAMESPACE + bluetooth_constants.ADAPTER_NAME
# acquire an adapter proxy object and its Adapter1 interface so we can
#call its methods

    adapter_object = bus.get_object(bluetooth_constants.BLUEZ_SERVICE_NAME,
        adapter_path)
    adapter_interface=dbus.Interface(adapter_object,
        bluetooth_constants.ADAPTER_INTERFACE)

# register signal handler functions so we can asynchronously report
#discovered devices

# InterfacesAdded signal is emitted by BlueZ when an advertising packet
#from a device it doesn't
# already know about is received
    bus.add_signal_receiver(interfaces_added,
        dbus_interface = bluetooth_constants.DBUS_OM_IFACE,
        signal_name = "InterfacesAdded")
    
    # PropertiesChanged signal is emitted by BlueZ when something re: a
    #device already encountered
    # changes e.g. the RSSI value
    bus.add_signal_receiver(properties_changed,
        dbus_interface = bluetooth_constants.DBUS_PROPERTIES,
        signal_name = "PropertiesChanged",
        path_keyword = "path")
    
    mainloop = GLib.MainLoop()
    adapter_interface.StartDiscovery(byte_arrays=True)
    mainloop.run()
    
# dbus initialisation steps
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()
# ask for a list of devices already known to the BlueZ daemon
print("Listing devices already known to BlueZ:")
get_known_devices(bus)
print("Scanning")
discover_devices(bus)