#!/usr/bin/python3
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib

# Need an event loop to recieve method calls in the same way we 
# recieve signals. 

mainloop = None

# We inherit the below class 
class Calculator(dbus.service.Object):
    # constructor
    def __init__(self, bus):
        self.path = '/com/example/calculator'
        dbus.service.Object.__init__(self, bus, self.path)

    # This line above the function is a decaratior
    #arguments are interface nae, type specifer for input ten one four outputs
    
    @dbus.service.method("com.example.calculator_interface",
        in_signature='ii',
        out_signature='i')
    def Add(self, a1, a2):
        sum = a1 +a2
        print(a1," + ",a2," = ",sum)
        return sum
        
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()

# Create the class with our implemnted callable mehtod
calc = Calculator(bus)

mainloop = GLib.MainLoop()
print("waiting for some calculations to do....")
mainloop.run()