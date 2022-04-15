import AdvertisementUtil
import struct

class Broadcast(AdvertisementUtil.Advertisement):


    def __init__(self, bus, index, localName, binaryData, latitude, longitude):
        AdvertisementUtil.Advertisement.__init__(self, bus, index, 'peripheral', localName)

        if binaryData == None:
            pass
        latitude = (self.LongLat2Unit(latitude)) 
        longitude = (self.LongLat2Unit(longitude))
        packet = struct.pack('ll', longitude, latitude)
        # Whilst its not the proper way to use UUID and gatt characteristics
        # It works.
        print(f"raw hex{packet.hex()}")
        testPacket = struct.unpack('ll', packet)
        print(f"size is : {len(packet)}")
        print(testPacket)
        
        self.add_service_data('9999', packet)

    # Converts decimal longlat to our 10cm units
    def LongLat2Unit(self, value):
        return int((value * 1000000))

    def Unit2LongLat(self, value):
        return float((value / 1000000))

