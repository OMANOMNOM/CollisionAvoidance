import py_compile

class Uav:
    def __init__(self, name, macAddress = "", latitude = 0, longitude = 0, altitude= 0 , curVelocity = 0):
        self.name = name
        self.macAddress = macAddress    
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.curVelocity = curVelocity
