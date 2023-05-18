import random
import math
import pymunk

from pymunk.vec2d import Vec2d

# Local imports
import constants

from laser_sensor import LaserSensor
from fuzzy import RobotFuzzySystem

# Have the same results with every run of the simulation
random.seed(1)


def random_sign():
    return 1 if random.randint(0, 2) < 1 else -1


class SRobot: 
    MASS = 0.65  # kg
    RADIUS = 10  # cm

    def __init__(self, space, start_pos, goal_pos):
        # Save the space the robots are going to be placed in
        self.space = space

        # All of the robots know the goal or the nest position
        self.goal_pos = goal_pos

        # Create the robot in the vicinity of the starting point
        x = start_pos[0] 
        y = start_pos[1] 

        # Create the body of the robot
        self.body = self.__add_robot_body(space, position=(x, y))

        # Attach a LaserSensor to it
        self.sensor = LaserSensor(position=(x, y), body_angle=self.body.angle)

        # Attach the fuzzy controller to it
        self.flc = RobotFuzzySystem()

        # Add vtras and vrot variables 
        self.vtras = 0
        self.vrot = 0

    def update_vtras(self, vtras, angle):
        self.body.velocity = (vtras, 0) 
        self.body.angle = angle
        
        self.vtras = vtras
        self.vrot = 0

        # Make the movement
        self.space.step(1 / constants.FPS)

        # Update the position of the sensor
        self.sensor.update_position(self.body.position, self.body.angle)  

    def update_vrot(self, vrot):
        self.body.velocity = (self.vtras, 0) 
        self.body.angular_velocity = vrot  # in radians

        # Make the movement
        self.space.step(1 / constants.FPS)

        # Update the position of the sensor
        self.sensor.update_position(self.body.position, self.body.angle)  

    def __add_robot_body(self, space, position):
        """Create and add to the space a box shape for the robot body.
        
        size[cm]; mass[kg]"""
    
        body = pymunk.Body()
        body.position = position

        shape = pymunk.Circle(body, self.RADIUS)
        
        # Add the attributes of the robot's body
        shape.mass = self.MASS
        shape.friction = 1
        shape.color = constants.COLOR["grey"]

        # Add the body to the space
        space.add(body, shape)

        return body
    
    def get_velocities(self):
        """
        Returns:
            (float, float): Returns translational and roational velocities (in
            this order) once they are computed by the FLC.
        """
        distances = self.sensor.get_reading()
        n = len(distances)

        # Get the minimum distance for readings of the left zone
        left_dist = min(distances[0 : (n // 3)])

        # Get the minimum distance for readings of the front zone
        front_dist = min(distances[(n // 3) : (2 * n // 3 + n%3)])

        # Get the minimum distance for readings of the right zone
        right_dist = min(distances[(2 * n // 3 + n%3) : n])

        # Compute the distance to goal from the robot
        dist = math.sqrt((self.body.position[0] - self.goal_pos[0]) ** 2  
                         + (self.body.position[1] - self.goal_pos[1]) ** 2)
        
        # Save the new velocities
        self.vtras, self.vrot = self.flc.evaluate(inp_left=left_dist,
                                                  inp_front=front_dist,
                                                  inp_right=right_dist,
                                                  inp_ang=self.body.angle,
                                                  inp_dist=dist)
        
        return self.vtras, self.vrot