import AdvertisementUtil

class Broadcast(AdvertisementUtil.Advertisement):

    def __init__(self, bus, index, localName, binaryData):
        AdvertisementUtil.Advertisement.__init__(self, bus, index, 'peripheral', localName)

        # All data is put into this.
        # Whilst its not the proper way to use UUID and gatt characteristics
        # It works.        
        self.add_service_data('9999', binaryData)

