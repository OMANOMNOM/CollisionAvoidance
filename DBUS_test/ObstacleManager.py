#!/usr/bin/python3
from gi.repository import GLib
#import bluetooth_utils as bluetooth_utils
import bluetooth_constants
import dbus
import dbus.mainloop.glib
import sys
import struct 
import Uav
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
class ObstacleManager():
    def __init__(self, scanTime):
        scanTime = scanTime * 1000
        self.droneHistory = []
        self.KnownDrones = []
        # dbus initialisation steps
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()

        print("Scanning")
        self.discover_devices(bus, scanTime)
        #print(f'Number of bluetooth devices found is: {len(devices)}')

    def byteArrayToHexString(self, bytes):
        hex_string = ""
        for byte in bytes:
            hex_byte = '%02X' % byte
            hex_string = hex_string + hex_byte
        return hex_string

    def dbus_to_python(self, data):
        if isinstance(data, dbus.String):
            data = str(data)
        if isinstance(data, dbus.ObjectPath):
            data = str(data)
        elif isinstance(data, dbus.Boolean):
            data = bool(data)
        elif isinstance(data, dbus.Int64):
            data = int(data)
        elif isinstance(data, dbus.Int32):
            data = int(data)
        elif isinstance(data, dbus.Int16):
            data = int(data)
        elif isinstance(data, dbus.UInt16):
            data = int(data)
        elif isinstance(data, dbus.Byte):
            data = int(data)
        elif isinstance(data, dbus.Double):
            data = float(data)
        elif isinstance(data, dbus.Array):
            data = [self.dbus_to_python(value) for value in data]
        elif isinstance(data, dbus.Dictionary):
            new_data = dict()
            for key in data.keys():
                new_data[key] = self.dbus_to_python(data[key])
            data = new_data
        return data

    def device_address_to_path(self, bdaddr, adapter_path):
        # e.g.convert 12:34:44:00:66:D5 on adapter hci0 to /org/bluez/hci0/dev_12_34_44_00_66_D5
        path = adapter_path + "/dev_" + bdaddr.replace(":","_")
        return path

    def get_name_from_uuid(self, uuid):
        if uuid in bluetooth_constants.UUID_NAMES:
            return bluetooth_constants.UUID_NAMES[uuid]
        else:
            return "Unknown"

    def text_to_ascii_array(self, text):
        ascii_values = []
        for character in text:
            ascii_values.append(ord(character))
        return ascii_values

    def print_properties(self, props):
        # dbus.Dictionary({dbus.String('SupportedInstances'): dbus.Byte(4, variant_level=1), dbus.String('ActiveInstances'): dbus.Byte(1, variant_level=1)}, signature=dbus.Signature('sv'))
        for key in props:
            print(key+"="+str(props[key]))

    # Signal called once a devices properites changes. Address will always stay same however
    def properties_changed(self, interface, changed, invalidated, path):
        if interface != bluetooth_constants.DEVICE_INTERFACE:
            return
        if path in devices:
            devices[path] = dict(devices[path].items())
            devices[path].update(changed.items())
        else:
            devices[path] = changed
        
        dev = devices[path]
        #printDeviceData(dev, path)
        #self.printDroneDetails(dev, "updated")
        tempDrone = self.extracPacket(dev)
        if tempDrone != None:
            self.KnownDrones = [tempDrone]

    def interfaces_removed(self, path, interfaces):
        # interfaces is an array of dictionary strings in this signal
        if not bluetooth_constants.DEVICE_INTERFACE in interfaces:
            return
        #if path in devices:
            #dev = devices[path]
            #if 'Address' in dev:
            #    print("DEL bdaddr: ", self.dbus_to_python(dev['Address']))
            #else:
            #    print("DEL path : ", path)  
            #    print("------------------------------")
            #del devices[path]

    # Called for each new device discovered
    def interfaces_added(self, path, interfaces):
        # Not all objects returned are discovered devices
        if not bluetooth_constants.DEVICE_INTERFACE in interfaces:
            return
        device_properties = interfaces[bluetooth_constants.DEVICE_INTERFACE]
        if path not in devices:
            devices[path] = device_properties
            dev = devices[path]
            #printDeviceData(dev, path)
            #self.printDroneDetails(dev, "added")
            tempDrone = self.extracPacket(dev)
            if tempDrone != None:
                self.KnownDrones = [tempDrone]


    def discovery_timeout(self):
        global adapter_interface
        global mainloop
        global timer_id
        GLib.source_remove(timer_id)
        mainloop.quit()
        adapter_interface.StopDiscovery()
        bus = dbus.SystemBus()
        bus.remove_signal_receiver(self.interfaces_added,"InterfacesAdded")
        bus.remove_signal_receiver(self.interfaces_added,"InterfacesRemoved")
        bus.remove_signal_receiver(self.properties_changed,"PropertiesChanged")
        return True

    def extracPacket(self, drone):
        if 'Name' in drone and 'Drone' in drone['Name']:
            packet = self.dbus_to_python(drone['ServiceData'])
            array = packet.values()
            array = list(packet.values())[0]
            tempstr = ""
            for i in array:
                if i <= 15:
                    tempstr += "0"
                tempstr += hex(i)[2:]
            data = bytes.fromhex(tempstr)
            #print(data.hex('-'))
            long, lat, altitude, velX, velY, velZ = struct.unpack('iiHhhh', bytes(data))
            return Uav.Uav(drone['Name'], "", lat, long, altitude, [velX, velY, velZ])
 
    def printDroneDetails(self, drone, state):
        if 'Name' in drone and 'Drone' in drone['Name']:
            print('------ *£* -----')
            print("WE found the drone")
            print(state)
            packet = self.dbus_to_python(drone['ServiceData'])
            
            array = packet.values()
            array = list(packet.values())[0]
            tempstr = ""
            for i in array:
                if i <= 15:
                    tempstr += "0"
                tempstr += hex(i)[2:]
            data = bytes.fromhex(tempstr)
            #print(data.hex('-'))
            long, lat, altitude, velX, velY, velZ = struct.unpack('iiHhhh', bytes(data))
            print("NEW name : ", self.dbus_to_python(drone['Name']))
            print(f"long: {long}")
            print(f"lat: {lat}")
            print(f"altitude: {altitude}")
            print(f'velX: {velX}')
            print(f"velY: {velY}")
            print(f"VelZ: {velZ}")
            self.droneHistory.append({'Name': drone['Name'], 'macAddress': '', 'Longitude' : long, 'Latitude' : lat, 'Altitude': altitude, 'VelX' : velX, 'VelY' : velY, 'VelZ': velZ})
            #print(f'lat : {lat}')

    def printDeviceData(self, dev, path):
        print("CHG path :", path)
        if 'Address' in dev:
            print("NEW bdaddr: ", self.dbus_to_python(dev['Address']))
        if 'Name' in dev:
            print("NEW name : ", self.dbus_to_python(dev['Name']))
        if 'RSSI' in dev:
            print("NEW RSSI : ", self.dbus_to_python(dev['RSSI']))
        print("------------------------------")

    # TOOD: FILTER THE DISCOVERIES
    #def setDisverFilter(bus):
    #    global adapter_interface
    #    adapter_object = bus.get_object(bluetooth_constants.BLUEZ_SERVICE_NAME,adapter_path)
    #    adapter_interface=dbus.Interface(adapter_object,bluetooth_constants.ADAPTER_INTERFACE)
    #    adapter_interface.SetDiscoverFilter([])

    # Stars the device discovery process
    def discover_devices(self, bus, timeout):
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

        # Can only BLE and not bluetooth classic. 
        adapter_interface.SetDiscoveryFilter({'Transport': "le"})

    #-------------------------------
        bus.add_signal_receiver(self.interfaces_added,dbus_interface = bluetooth_constants.DBUS_OM_IFACE, signal_name = "InterfacesAdded")
        
        # InterfacesRemoved signal is emitted by BlueZ when a device "goes away"
        bus.add_signal_receiver(self.interfaces_removed, dbus_interface = bluetooth_constants.DBUS_OM_IFACE, signal_name = "InterfacesRemoved")

        # PropertiesChanged signal is emitted by BlueZ when something re: a device already encountered
        # changes e.g. the RSSI value
        bus.add_signal_receiver(self.properties_changed, dbus_interface = bluetooth_constants.DBUS_PROPERTIES, signal_name = "PropertiesChanged", path_keyword = "path")

        mainloop = GLib.MainLoop()
        timer_id = GLib.timeout_add(timeout, self.discovery_timeout)
        adapter_interface.StartDiscovery(byte_arrays=True)
        
        mainloop.run()

