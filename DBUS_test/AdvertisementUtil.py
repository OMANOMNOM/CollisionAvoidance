#!/usr/bin/python3
# Broadcasts connectable advertising packets
import bluetooth_constants
import bluetooth_exceptions
import dbus
import dbus.exceptions
import dbus.service
import dbus.mainloop.glib
import sys
from gi.repository import GLib
import time
import threading
sys.path.insert(0, '.')

#bus = None
#adapter_path = None
#adv_mgr_interface = None

# Unfotuantly the is no convient way to update the data sent in an advertisement. 
# From the docs - "The properties of this object are parsed when it is registered, and any changes are ignored"
# So A new advertisment is updated, registered and released once a second.

# Create proxy object. This is an exported object. 
class Advertisement(dbus.service.Object):
    PATH_BASE = '/org/bluez/ldsg/advertisement'

    # Implement a class that defines the advertiement object. 
    def __init__(self, bus, index, advertising_type, localName):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.ad_type = advertising_type
        self.service_uuids = None
        self.manufacturer_data = None
        self.solicit_uuids = None
        self.service_data = None
        self.local_name = localName
        self.include_tx_power = True
        self.data = None
        self.discoverable = True
        self.MaxInterval = 500
        self.MinInterval = 1000
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        properties = dict()
        properties['Type'] = self.ad_type
        if self.service_uuids is not None:
            properties['ServiceUUIDs'] = dbus.Array(self.service_uuids,signature='s')
        if self.solicit_uuids is not None:
            properties['SolicitUUIDs'] = dbus.Array(self.solicit_uuids,signature='s')
        if self.manufacturer_data is not None:
            properties['ManufacturerData'] = dbus.Dictionary(self.manufacturer_data, signature='qv')
        if self.service_data is not None:
                properties['ServiceData'] = dbus.Dictionary(self.service_data,signature='sv')
        if self.local_name is not None:
            properties['LocalName'] = dbus.String(self.local_name)
        if self.discoverable is not None and self.discoverable == True:
            properties['Discoverable'] = dbus.Boolean(self.discoverable)
        if self.include_tx_power:
            properties['Includes'] = dbus.Array(["tx-power"], signature='s')
        if self.data is not None:
            properties['Data'] = dbus.Dictionary(self.data, signature='yv')
        if self.MaxInterval is not None:
            properties['MaxInterval'] = dbus.UInt32(self.MaxInterval)
        if self.MinInterval is not None:
            properties['MinInterval'] = dbus.UInt32(self.MinInterval)

        print(properties)
        return {bluetooth_constants.ADVERTISING_MANAGER_INTERFACE:properties}

    def get_path(self):
        return dbus.ObjectPath(self.path)

    ## EXPERIMENTAL - Doesn't work on the pi only on the blade
    # TODO update bluez on pis to 5.6
    #def add_data(self, ad_type, data):
    #    if not self.data:
    #        self.data = dbus.Dictionary({}, signature='yv')
    #    self.data[ad_type] = dbus.Array(data, signature='y')


    def add_service_data(self, uuid, data):
        if not self.service_data:
            self.service_data = dbus.Dictionary({}, signature='sv')
        # array of bytes
        self.service_data[uuid] = dbus.Array(data, signature='y')


    # Export method, so bluez can call this over dbus
    @dbus.service.method(bluetooth_constants.DBUS_PROPERTIES,in_signature='s',out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != bluetooth_constants.ADVERTISEMENT_INTERFACE:
            raise bluetooth_exceptions.InvalidArgsException()
        return self.get_properties()[bluetooth_constants.ADVERTISING_MANAGER_INTERFACE]
    

    # Export Method
    # TODO This method isn't being called
    @dbus.service.method(bluetooth_constants.ADVERTISING_MANAGER_INTERFACE,
        in_signature='',
        out_signature='')
    def Release(self):
        print('%s: Released' % self.path)
