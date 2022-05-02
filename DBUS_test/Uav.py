import py_compile

class Uav:
    def __init__(self, name, macAddress = "", latitude = 0, longitude = 0, altitude= 0 , curVelocity = 0):
        self.name = name
        self.macAddress = macAddress    
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.curVelocity = curVelocity

    def printDrone(self):
        print(f"Name : {self.name}")
        print(f"long: {self.longitude} lat: {self.latitude} altitude: {self.altitude}")
        #print(f'velX: {self}')
        #    print(f"velY: {velY}")
        #    print(f"VelZ: {velZ}")
