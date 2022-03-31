import AdvertisementUtil

class Broadcast(AdvertisementUtil.Advertisement):

    def __init__(self, bus, index, localName):
        AdvertisementUtil.Advertisement.__init__(self, bus, index, 'peripheral', localName)
        ## What services this device offers
        #self.add_service_uuid('180D')
        #self.add_service_uuid('180F')
        # Manufactuer 2 octect code, and manufact data
        #self.add_manufacturer_data(0xffff, [0x00, 0x01, 0x02, 0x03])

        # UUID and its associated data
        #self.add_service_data('9999', [0x00, 0x01, 0x03, 0x04,0x01, 0x02, 0x03, 0x04, 0x00, 0x01, 0x02, 0x03, 0x04,0x01, 0x01, 0x04,0x01, 0x02, 0x03, 0x04,0x00,  0x00, 0x02, 0x03, 0x04, 0x00, 0x01 ])

        # Local name
        #self.add_local_name('Test')
        # Turn off to save bandwidth
        #self.include_tx_power = False
        # first number is type, second is value
        #self.add_data(0x26, [0x01, 0x01, 0x00])
