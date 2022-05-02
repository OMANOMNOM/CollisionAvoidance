#import sympy
import ObstacleManager
import Uav
import goal
import time 
import math
import Broadcast
from threading import Thread



# Long lat represent UAV starting position. Typically at zero 
# Interanally we use cms with coorinate centre where the real drone is.
# For now everything is planar
class TelloDone(Uav.Uav):
    def __init__(self, name, startX, startY, startZ):
        super().__init__(self, name)
        # virtual drone typically 15 meters in front of regualr drone
        self.x = startX
        self.y = startY
        self.z = startZ
        self.curGoalIndex = 0

        self.maxSpeed = 100
        self.obsMgr = None
        self.update()

    #Updates once a second
    def update(self):

        while True:
            #print("tick")
            starttime = time.time()
            print(f"Cur Position X:{self.x} Y:{self.y} Z:{self.z}")

            # Broadcast in 
            new_thread = Thread(target=self.broadcastIn)
            new_thread.start()


            #Wait a second
            time.sleep(1.0 - ((time.time() - starttime) % 1.0))
            new_thread.join()
            

    
    def broadcastIn(self):
        self.obsMgr = ObstacleManager.ObstacleManager(1)
        for i in self.obsMgr.KnownDrones:
            i.printDrone()
        #return self.obsMgr.

    """
    def PredictCollision():
        # Get all current obstacles 
        obsVel = [0, -1]
        obsPosPoint = Point(0,10)
        obsBubbleRadius = 1

        # Get state of Drone
        droneVel = [0, 0]
        dronePosPoint = Point(3,0)
        dronebubbleRadius = 3
        # Reduce A to a point and enlarge B by the radius of A
        obsBubbleRadius += dronebubbleRadius 

        #Calculate collision cone dimensiSSSSSons
        collisionBoundaries = Circle(obsPosPoint, obsBubbleRadius)
        print(collisionBoundaries.equation())

        # Generate CC
        tangentLines = collisionBoundaries.tangent_lines(dronePosPoint)
        collisonCone = Polygon(tangentLines[1].p1, tangentLines[1].p2, tangentLines[0].p2)
        # Scale collision cone for time horizon
        #print(collisonCone)

        # Translate CC by B
        collisonCone= collisonCone.translate(obsVel[0], obsVel[1])
        #print(collisonCone)

        #Check if absolute veloicty of A falls witihin CC ()
        VelVectorTip = Point(dronePosPoint.x + droneVel[0],  dronePosPoint.y + droneVel[1])
        print(VelVectorTip)
        if(collisonCone.encloses_point(VelVectorTip)):
            print("We have a inpending collision")
    """

    def EscapeManeuver():
        pass 

           

    """
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
    """
temp = TelloDone("Drone3", 0,0,0)