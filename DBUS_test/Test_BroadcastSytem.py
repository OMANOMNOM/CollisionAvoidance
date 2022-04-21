import unittest
import csv
import sys
import Broadcast
import Uav
class TestBroadcastSystem(unittest.TestCase):

    # Read in CSV file    
    def setUp(self):
        data = []
        if sys.argv[1] == 'b':
            print("Broadcasting")
            with open('DummyDrone.csv', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data.append(row)
            for i in data:
                print(f"{i['Name']} {i['Latitude']} {i['Longitude']} {i['Altitude']} {i['VelX']} {i['VelY']} {i['VelZ']}")
                Broadcast.broadcastOut(3, Uav.Uav(i['Name'], "", float(i['Latitude']), float(i['Longitude']), i['Altitude'], [int(i['VelX']), int(i['VelY']), int(i['VelZ'])]))

        else:
            print("this didn't work")

    def test_add(self):
        self.assertEqual(4,4)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

