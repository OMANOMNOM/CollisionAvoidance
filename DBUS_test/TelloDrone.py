import sympy
import ObstacleManager
import Uav
import goal
import time 
import math
import Broadcast
from threading import Thread
import tellopy
import random


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
        self.obsList = []
        self.drone = tellopy.Tello()
        self.startup()
        #self.update()
    

    def startup(self):
        #self.drone.subscribe(self.drone.EVENT_FLIGHT_DATA, self.handler)
        self.drone.connect()
        self.drone.wait_for_connection(60.0)
        self.drone.takeoff() 
        self.update() 

    #Updates once a second
    def update(self):
        while True:
            # We have to regularally send drone dummy commands to stop it from going into standby mode
            if self.drone != None:
                self.drone.down(0)
            print("---------tick-----------------")
            starttime = time.time()
            print(f"Cur Position X:{self.x} Y:{self.y} Z:{self.z}")

            # Broadcast in 
            new_thread = Thread(target=self.broadcastIn)
            new_thread.start()

            # Known drones from prevous tick
            for i in self.obsList:
                i.printDrone()

            # Check for collision from prevous tick
            for i in self.obsList:
                self.PredictCollision(i)

            #Wait for the remainder of tick
            time.sleep(1.0 - ((time.time() - starttime) % 1.0))
            new_thread.join()
            print('\n')

    def broadcastIn(self):
        self.obsMgr = ObstacleManager.ObstacleManager(1)
        if len(self.obsMgr.KnownDrones) > 0: 
            self.obsList = self.obsMgr.KnownDrones
            for i in self.obsMgr.KnownDrones:
                i.printDrone()

        #return self.obsMgr.

    def PredictCollision(self, drone):
        # Get all current obstacles 
        obsVel = [0, -1]
        #obsVel = [drone.curVelocity[0], drone.curVelocity[1]]
        obsPosPoint = sympy.Point(drone.latitude,drone.longitude)
        obsBubbleRadius = 75

        # Get state of Drone
        droneVel = [0, 0]
        #dronePosPoint = sympy.Point(self.x,self.y)
        dronePosPoint = sympy.Point(-500,-400)
        dronebubbleRadius = 75

        # If on the same plane
        if self.altitude == drone.altitude:
            # Reduce A to a point and enlarge B by the radius of A
            obsBubbleRadius += dronebubbleRadius 

            # Check drone isn't already within collision volume
            if( dronePosPoint.distance(obsPosPoint) < obsBubbleRadius):
                print("we have a collision")
            else:
                #Calculate collision cone dimensiSSSSSons
                collisionBoundaries = sympy.Circle(obsPosPoint, obsBubbleRadius)
                #print(collisionBoundaries.equation())

                # Generate CC
                tangentLines = collisionBoundaries.tangent_lines(dronePosPoint)
                collisonCone = sympy.Polygon(tangentLines[1].p1, tangentLines[1].p2, tangentLines[0].p2)
                # Scale collision cone for time horizon
                #print(collisonCone)

                # Translate CC by B
                collisonCone= collisonCone.translate(obsVel[0], obsVel[1])
                #print(collisonCone)

                #Check if absolute veloicty of A falls witihin CC ()
                VelVectorTip = sympy.Point(dronePosPoint.x + droneVel[0],  dronePosPoint.y + droneVel[1])
                #print(VelVectorTip)
                if(collisonCone.encloses_point(VelVectorTip)):
                    print("We have a inpending collision")

    def EscapeManeuver(self, collisonCone, dronePosPoint):
        # Try forwards
        escapeTrajectoryLength = 200
        while true:
            potentialDestinationForward = sympy.Point(dronePosPoint.x, dronePosPoint.y + escapeTrajectoryLength )
            if collisonCone.encloses_point(potentialDestinationForward) == False:
                self.y + 200
                self.drone.forward(200)
                self.drone.sleep(5)
                return
            potentialDestinationBackwards = sympy.Point(dronePosPoint.x, dronePosPoint.y - escapeTrajectoryLength)
            if collisonCone.encloses_point(potentialDestinationBackwards) == False:
                self.y + -200
                self.drone.backward(200)
                self.drone.sleep(5)
                return
            potentialDestinationLeft = sympy.Point(dronePosPoint.x - escapeTrajectoryLength, dronePosPoint.y)
            if collisonCone.encloses_point(potentialDestinationLeft) == False:
                self.x - 200
                self.drone.left(200)
                self.drone.sleep(5)
                return
            potentialDestinationRight = sympy.Point(dronePosPoint.x + escapeTrajectoryLength, dronePosPoint.y )
            if collisonCone.encloses_point(potentialDestinationLeft) == False:
                self.x + 200
                self.drone.right(200)
                self.up(100)
                self.z = 200
                self.drone.sleep(5)
                return
            escapeTrajectoryLength += 100

           

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