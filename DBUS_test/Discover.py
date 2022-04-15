#!/usr/bin/python3
from gi.repository import GLib
import bluetooth_utils
import bluetooth_constants
import dbus
import dbus.mainloop.glib
import sys
import struct 
sys.path.insert(0, '.')

# When bluez performs scanning, an object representing it is created by bluez. It is exported
# To the d-bus system bus. It is a managed object
# A interfacesAdded signal is emitted. 
# Devices once scanned won't be scanned again. 
# Bluez has a root object with implments an object manager
# Objects are forgottn after a certain amount of time.

# Get the object
adapter_interface = None
mainloop = None
timer_id = None

devices = {}

# Signal called once a devices properites changes. Address will always stay same however
def properties_changed(interface, changed, invalidated, path):
    if interface != bluetooth_constants.DEVICE_INTERFACE:
        return
    if path in devices:
        devices[path] = dict(devices[path].items())
        devices[path].update(changed.items())
    else:
        devices[path] = changed

    dev = devices[path]
    #printDeviceData(dev, path)
    printDroneDetails(dev)

def interfaces_removed(path, interfaces):
    # interfaces is an array of dictionary strings in this signal
    if not bluetooth_constants.DEVICE_INTERFACE in interfaces:
        return
    if path in devices:
        dev = devices[path]
        if 'Address' in dev:
            print("DEL bdaddr: ", bluetooth_utils.dbus_to_python(dev['Address']))
        else:
            print("DEL path : ", path)  
            print("------------------------------")
        del devices[path]

# Called for each new device discovered
def interfaces_added(path, interfaces):
    # Not all objects returned are discovered devices
    if not bluetooth_constants.DEVICE_INTERFACE in interfaces:
        return
    device_properties = interfaces[bluetooth_constants.DEVICE_INTERFACE]
    if path not in devices:
        devices[path] = device_properties
        dev = devices[path]
        #printDeviceData(dev, path)
        printDroneDetails(dev)

def discovery_timeout():
    global adapter_interface
    global mainloop
    global timer_id
    GLib.source_remove(timer_id)
    mainloop.quit()
    adapter_interface.StopDiscovery()
    bus = dbus.SystemBus()
    bus.remove_signal_receiver(interfaces_added,"InterfacesAdded")
    bus.remove_signal_receiver(interfaces_added,"InterfacesRemoved")
    bus.remove_signal_receiver(properties_changed,"PropertiesChanged")
    return True

def printDroneDetails(drone):
    if 'Name' in drone and 'local' in drone['Name']:
        print('------ *£* -----')
        print("WE found the drone")
        packet = bluetooth_utils.dbus_to_python(drone['ServiceData'])
        print(packet)
        array = packet.values()
        array = list(packet.values())[0]
        tempstr = ""
        for i in array:
            tempstr += hex(i)[2:]
        print(tempstr)

        data = bytes.fromhex(tempstr)
        long, lat = struct.unpack('ii', bytes(data))
        print(long)
        print(lat)
        #print(f'long : {long}')
        #print(f'lat : {lat}')

def printDeviceData(dev, path):
    print("CHG path :", path)
    if 'Address' in dev:
        print("NEW bdaddr: ", bluetooth_utils.dbus_to_python(dev['Address']))
    if 'Name' in dev:
        print("NEW name : ", bluetooth_utils.dbus_to_python(dev['Name']))
    if 'RSSI' in dev:
        print("NEW RSSI : ", bluetooth_utils.dbus_to_python(dev['RSSI']))
    print("------------------------------")

# TOOD: FILTER THE DISCOVERIES
#def setDisverFilter(bus):
#    global adapter_interface
#    adapter_object = bus.get_object(bluetooth_constants.BLUEZ_SERVICE_NAME,adapter_path)
#    adapter_interface=dbus.Interface(adapter_object,bluetooth_constants.ADAPTER_INTERFACE)
#    adapter_interface.SetDiscoverFilter([])

# Stars the device discovery process
def discover_devices(bus, timeout):
    global adapter_interface
    global mainloop
    global timer_id
    adapter_path = bluetooth_constants.BLUEZ_NAMESPACE + bluetooth_constants.ADAPTER_NAME

    # acquire an adapter proxy object and its Adapter1 interface so we cancall its methods
    adapter_object = bus.get_object(bluetooth_constants.BLUEZ_SERVICE_NAME,adapter_path)
    adapter_interface=dbus.Interface(adapter_object,bluetooth_constants.ADAPTER_INTERFACE)
    # register signal handler functions so we can asynchronously report discovered devices
    # InterfacesAdded signal is emitted by BlueZ when an advertising packetfrom a device it doesn't
    # already know about is received
    bus.add_signal_receiver(interfaces_added,dbus_interface = bluetooth_constants.DBUS_OM_IFACE, signal_name = "InterfacesAdded")
    
    # InterfacesRemoved signal is emitted by BlueZ when a device "goes away"
    bus.add_signal_receiver(interfaces_removed, dbus_interface = bluetooth_constants.DBUS_OM_IFACE, signal_name = "InterfacesRemoved")

    # PropertiesChanged signal is emitted by BlueZ when something re: a device already encountered
    # changes e.g. the RSSI value
    bus.add_signal_receiver(properties_changed, dbus_interface = bluetooth_constants.DBUS_PROPERTIES, signal_name = "PropertiesChanged", path_keyword = "path")

    mainloop = GLib.MainLoop()
    timer_id = GLib.timeout_add(timeout, discovery_timeout)
    adapter_interface.StartDiscovery(byte_arrays=True)
    
    mainloop.run()

if (len(sys.argv) != 2):
    print("usage: python3 client_discover_devices.py [scantime (secs)]")
    sys.exit(1)

scantime = int(sys.argv[1]) * 1000

# dbus initialisation steps
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()
print("Scanning")
discover_devices(bus, scantime)
print(len(devices))