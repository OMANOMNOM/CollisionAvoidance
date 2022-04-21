import AdvertisementUtil
import struct
import Uav
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

class Broadcast(AdvertisementUtil.Advertisement):

    # Packets Definition 
    # Latitude - 4 bytes int
    # Longitude - 4 bytes int
    # Altitude - 2 bytes unsigned short
    # CurVelocity - 3 variables(x,y,z) 2 bytes each
    def __init__(self, bus, index, drone, binaryData = None):
        AdvertisementUtil.Advertisement.__init__(self, bus, index, 'peripheral', drone.name)
        if binaryData != None:
            pass
        else:
            latitude = (self.LongLat2Unit(drone.latitude)) 
            longitude = (self.LongLat2Unit(drone.longitude))
            altitude = (self.AltConversion(drone.altitude))
            curVelocity = drone.curVelocity
            packet = struct.pack('iiHhhh', latitude, longitude, altitude, curVelocity[0], curVelocity[1], curVelocity[2])
            
        #printPacketHex(packet)
        self.add_service_data('9999', packet)

    # Converts decimal longlat to our 10cm units
    def LongLat2Unit(self, value):
        return int((value * 1000000))

    def AltConversion(self, value):
        return int(value)

    def Unit2LongLat(self, value):
        return float((value / 1000000))

    def printPacketHex(self, packet):
        print(f"raw hex: {packet.hex('-')}")


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
    #print("Registering advertisement",adv.get_path())
    adv_mgr_interface.RegisterAdvertisement(adv.get_path(), {},
        reply_handler=register_ad_cb,
        error_handler=register_ad_error_cb)


def broadcastOut(timer  = 5, testUAV = Uav.Uav(f"Drone3", "69", 56, -22, 10, [1,0,0])):
    global adv
    global adv_mgr_interface

    sys.path.insert(0, '.')
    global bus
    global adapter_path
    global adv_mgr_interface
    global mainloop
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    # we're assuming the adapter supports advertising
    adapter_path = bluetooth_constants.BLUEZ_NAMESPACE + bluetooth_constants.ADAPTER_NAME
    #print(adapter_path)



    # Get advertising manager
    adv_mgr_interface = dbus.Interface(bus.get_object(bluetooth_constants.BLUEZ_SERVICE_NAME,adapter_path), bluetooth_constants.ADVERTISING_MANAGER_INTERFACE)
    # we're only registering one advertisement object so index (arg2) is hard
    #coded as 

    # We create an advertising object and indicate peripheral. I would change this to broadcast
    adv = Broadcast(bus, 0, testUAV)
    start_advertising()
    print("Advertising as "+ adv.local_name)
    mainloop = GLib.MainLoop()

    threading.Thread(target=shutdown, args=(timer,)).start()
    # Execution stops here until loop is mainloop, hence a new thread for the timer is required
    mainloop.run()

    adv_mgr_interface.UnregisterAdvertisement(adv)
    #print('Advertisement unregistered')
    dbus.service.Object.remove_from_connection(adv)
    #print("Execution has stopped")