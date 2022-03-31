#!/usr/bin/python3

# 1. Import dbus
import dbus

# 2. Connect to the DBus system bus
bus = dbus.SystemBus()

# 3. Create a proxy object
    # proxy of an object of a service
proxy = bus.get_object('org.freedesktop.hostname1','/org/freedesktop/hostname1')

# 3. Get a refernce to our selected interface
interface = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')

all_props = interface.GetAll('org.freedesktop.hostname1')
print(all_props)

print("----------------")
# 5. Call the interfaces get method with suitable arguemnts
hostname = interface.Get('org.freedesktop.hostname1','Hostname')
print("The host name is ",hostname)