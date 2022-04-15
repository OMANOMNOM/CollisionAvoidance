import AdvertisementUtil
import struct

class Broadcast(AdvertisementUtil.Advertisement):


    def __init__(self, bus, index, localName, binaryData, latitude, longitude):
        AdvertisementUtil.Advertisement.__init__(self, bus, index, 'peripheral', localName)

        if binaryData == None:
            pass
        latitude = (self.LongLat2Unit(latitude)) 
        longitude = (self.LongLat2Unit(longitude))
        packet = struct.pack('ii', latitude, longitude)
        
        print(f"raw hex {packet.hex('-')}")
        #print(type(packet))
        #testPacket = struct.unpack('l', packet)
        #print(testPacket)

        #arr = [56, 255, 255, 255]
        #temp = ""
        #for i in arr:
        #    temp += hex(int(i))[2:]

        #print(temp)
        #sds = bytes.fromhex(temp)
        #testPacket = struct.unpack('i', sds)
        #print(f" our byte test is {testPacket}")
        
        self.add_service_data('9999', packet)

    # Converts decimal longlat to our 10cm units
    def LongLat2Unit(self, value):
        return int((value * 1000000))

    def Unit2LongLat(self, value):
        return float((value / 1000000))

