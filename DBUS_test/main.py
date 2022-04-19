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
import Broadcast
import struct
import Uav

sys.path.insert(0, '.')
bus = None
adapter_path = None
adv_mgr_interface = None

# Success callback
def register_ad_cb():
    print('Advertisement registered OK')

# Failure to advertise callback
def register_ad_error_cb(error):
    print('Error: Failed to register advertisement: ' + str(error))
    mainloop.quit()

def shutdown(timeout):
    print('Advertising for {} seconds...'.format(timeout))
    time.sleep(timeout)
    mainloop.quit()

def start_advertising():
    global adv
    global adv_mgr_interface
    # Call registerAdvertisemnt, passing in our proxy object and callbacks.
    print("Registering advertisement",adv.get_path())
    adv_mgr_interface.RegisterAdvertisement(adv.get_path(), {},
        reply_handler=register_ad_cb,
        error_handler=register_ad_error_cb)


dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()
# we're assuming the adapter supports advertising
adapter_path = bluetooth_constants.BLUEZ_NAMESPACE + bluetooth_constants.ADAPTER_NAME
print(adapter_path)
timer = 15
# Get advertising manager
adv_mgr_interface = dbus.Interface(bus.get_object(bluetooth_constants.BLUEZ_SERVICE_NAME,adapter_path), bluetooth_constants.ADVERTISING_MANAGER_INTERFACE)
# we're only registering one advertisement object so index (arg2) is hard
#coded as 

for i in range(0,5):

    testUAV = Uav.Uav("Drone1", "69", 56, -22, 10, [1,0,0])
    # We create an advertising object and indicate peripheral. I would change this to broadcast
    adv = Broadcast.Broadcast(bus, 0, testUAV)
    start_advertising()
    print("Advertising as "+ adv.local_name)
    mainloop = GLib.MainLoop()

    threading.Thread(target=shutdown, args=(timer,)).start()
    # Execution stops here until loop is mainloop, hence a new thread for the timer is required
    mainloop.run()

    adv_mgr_interface.UnregisterAdvertisement(adv)
    #print('Advertisement unregistered')
    dbus.service.Object.remove_from_connection(adv)
    print("Execution has stopped")