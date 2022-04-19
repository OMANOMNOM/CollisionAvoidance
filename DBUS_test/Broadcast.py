import AdvertisementUtil
import struct
import Uav

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