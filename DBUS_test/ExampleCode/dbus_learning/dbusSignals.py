import dbus
import dbus.mainloop.glib
from gi.repository import GLib
mainloop = None

def greeting_signal_received(greeting):
    print(greeting)

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

# Connect to system bus
bus = dbus.SystemBus()

#Register to recieve signal
bus.add_signal_receiver(greeting_signal_received,
    dbus_interface = "com.example.greeting",
    signal_name = "GreetingSignal")

#Start main loop
mainloop = GLib.MainLoop()
mainloop.run()