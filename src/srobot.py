import math
import pymunk

from pymunk.vec2d import Vec2d

# Local imports
import constants
import log

from laser_sensor import LaserSensor
from fuzzy import RobotFuzzySystem


class SRobot: 
    MASS = 0.65  # kg
    RADIUS = 10  # cm

    def __init__(self, space, start_pos, start_angle, goal_pos):
        # Create and save a logger for this class 
        self.logger = log.create_logger(name=self.__class__.__name__,
                                        level=log.LOG_INFO)

        # Save the space the robots are going to be placed in
        self.space = space

        # All of the robots know the goal or the nest position
        self.goal_pos = goal_pos

        # Create the body of the robot
        self.body = self.__add_robot_body(space, 
                                          position=start_pos, 
                                          start_angle=start_angle)

        # Attach a LaserSensor to it
        self.sensor = LaserSensor(position=start_pos, body_angle=self.body.angle)

        # Attach the fuzzy controller to it
        self.flc = RobotFuzzySystem()

        # Add vtras and vrot variables 
        self.vtras = 0
        self.vrot = 0
    
    def move_to(self, target_pos):
        target_delta = target_pos - self.body.position
        turn = self.body.rotation_vector.cpvunrotate(target_delta).angle 
        self.body.angle = self.body.angle - turn

        dist = (target_pos - self.body.position).get_length_sqrd()

        # Drive the robot towards the target object
        if dist < 0.5 ** 2:
            # If the robot is close enough to the target object, stop
            self.body.velocity = 0, 0
        else:
            if target_delta.dot(self.body.rotation_vector) > 0.0:
                direction = 1.0
            else:
                direction = -1.0

            dv = Vec2d(10 * direction, 0.0)
            self.body.velocity = self.body.rotation_vector.cpvrotate(dv)

        self.space.step(1/constants.FPS)

        # Update the position of the sensor
        self.sensor.update_position(self.body.position, self.body.angle) 

    def rotate_to(self, angle):
        """Rotate the robot to a specific angle."""

        if ((self.body.angle - angle) % (2 * math.pi)) < 0.1:
            self.body.angular_velocity = 0
        else:
            if angle > 0:
                self.body.angular_velocity = math.pi/10
            else:
                self.body.angular_velocity = -math.pi/10

        self.space.step(1/constants.FPS)

        # Update the position of the sensor
        self.sensor.update_position(self.body.position, self.body.angle)

    def __add_robot_body(self, space, position, start_angle):
        """Create and add to the space a box shape for the robot body.
        
        size[cm]; mass[kg]"""
    
        body = pymunk.Body()
        body.position = position
        body.angle = start_angle

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
        
        self.logger.debug(f'New velocities: vtras = {self.vtras}, vrot = {self.vrot}')
        
        return self.vtras, self.vrot