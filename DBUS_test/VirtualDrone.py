import Uav
import goal
import time 
import math
import Broadcast
from threading import Thread

# Long lat represent UAV starting position. Typically at zero 
# Interanally we use cms with coorinate centre where the real drone is.
# For now everything is planar
class VirtualDrone(Uav.Uav):
    def __init__(self, name, startX, startY, startZ):
        super().__init__(self, name)
        # virtual drone typically 15 meters in front of regualr drone
        self.x = startX
        self.y = startY
        self.z = startZ
        self.curGoalIndex = 0
        self.goals = []
        self.goals.append(goal.Goal(500,500,50))
        self.goals.append(goal.Goal(500,-500,50))
        self.goals.append(goal.Goal(-500,-500,50))
        self.goals.append(goal.Goal(-500,500,50))
        self.maxSpeed = 100

        self.update()

    #Updates once a second
    def update(self):
        isCallable = True # we broadcast everyother loop
        starttime = time.time()
        while True:
            print("-----------tick------------")
            print(f"Cur Position X:{self.x} Y:{self.y}Z:{self.z}")
            if self.isAtGoal():
                if self.curGoalIndex+1 == len(self.goals):
                    print('Loop complete')
                    self.curGoalIndex = 0
                else:
                    self.curGoalIndex += 1
            self.goToGoal()
            # Broadcast position
            if isCallable:
                new_thread = Thread(target=self.broadcastvirtual)
                new_thread.start()
                isCallable = False
            else:
                isCallable = True
            #Broadcast.broadcastOut(2, Uav.Uav( "Drone3", "", self.x, self.y, 0, [0,0,0]))
            time.sleep(1.0 - ((time.time() - starttime) % 1.0))

    def broadcastvirtual(self):
        Broadcast.broadcastOut(1, Uav.Uav( "Drone3", "", self.x, self.y, 0, [0,0,0]))


    #Fly directly to goal in a linear fashion.
    def goToGoal(self):
        temp =  self.goals[self.curGoalIndex]
        distY = abs(self.y - temp.y)
        distX = abs(self.x - temp.x)
        # If distance between vd and goal is less than 5cm
        if math.sqrt(distX**2 + distY**2) < self.maxSpeed:
            self.x = temp.x
            self.y = temp.y
            #Move stright to goal position
        #else move towards goal
        if distY == 0:
            dx = self.maxSpeed
            dy = 0
        else:
            angl = (math.atan(distX/distY))
            dx = math.sin(angl)* self.maxSpeed
            dy = math.cos(angl) * self.maxSpeed
        if self.y < temp.y:
            self.y +=dy
        else:
            self.y -=dy
        if self.x < temp.x:
            self.x += dx
        else:
            self.x -= dx
    
    def isAtGoal(self):
        temp =  self.goals[self.curGoalIndex]
        if self.x == temp.x and self.y == temp.y:
            print("Reached current goal")
            return True
        return False

temp = VirtualDrone("Drone3", 0,0,0)