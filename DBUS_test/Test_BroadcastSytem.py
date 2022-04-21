import unittest
import csv
import sys
import Broadcast
from ObstacleManager import ObstacleManager
import Uav


# To run these tests you execute the program on two devices, broadcaster and listener.
# use b as a program argument for the broadcaster
# use l as a program argument for the Listener
# Using neither will result in an error
class TestBroadcastSystem(unittest.TestCase):
    # Read in CSV file    
    def setUp(self):
        self.dummyData = []
        with open('DummyDrone.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.dummyData.append(row)
        if sys.argv[1] == 'b':
            print("Broadcasting")
            for i in self.dummyData:
                #print(f"{i['Name']} {i['Latitude']} {i['Longitude']} {i['Altitude']} {i['VelX']} {i['VelY']} {i['VelZ']}")
                Broadcast.broadcastOut(3, Uav.Uav(i['Name'], "", float(i['Latitude']), float(i['Longitude']), i['Altitude'], [int(i['VelX']), int(i['VelY']), int(i['VelZ'])]))
        if sys.argv[1] == 'l':
            self.mgr = ObstacleManager(120)
            #print(self.dummyData)
            #print("-----------")
            #print(self.mgr.droneHistory)
            #Record in the packets into list
            

    def test_packetLoss(self):
        self.assertGreaterEqual(len(self.mgr.droneHistory),len(self.dummyData))

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

