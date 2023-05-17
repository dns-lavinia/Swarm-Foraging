import random
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

    def __init__(self, space, start_pos):
        # Create the robot in the vicinity of the starting point
        x = start_pos[0] 
        y = start_pos[1] 

        # Create the body of the robot
        self.body = self.__add_robot_body(space, position=(x, y))

        # Attach a LaserSensor to it
        self.sensor = LaserSensor(position=(x, y), body_angle=self.body.angle)

        # Attach the fuzzy controller to it
        # FIXME: Upon adding the fuzzy system, I get a runtime warning from
        # matlplotlib stating there are too many figures open at once (more than
        # 20)
        # self.flc = RobotFuzzySystem()
    
    # TODO: this function will be changed accordingly when RL will be added
    # source: https://github.com/viblo/pymunk/blob/master/pymunk/examples/tank.py 
    def update(self, space, dt, target_pos):
        """Update the position of the robot."""

        # Based on the reading the robot gets from the sensor, update the 
        # position -> this would be one of the FLCs
        self.sensor.get_reading()
        
        target_delta = target_pos - self.body.position
        turn = self.body.rotation_vector.cpvunrotate(target_delta).angle 
        self.body.angle = self.body.angle - turn

        # # Drive the robot towards the target object
        # if (target_pos - self.body.position).get_length_sqrd() < 30 ** 2:
        #     # If the robot is close enough to the target object, stop
        #     self.body.velocity = 0, 0
        # else:
        #     if target_delta.dot(self.body.rotation_vector) > 0.0:
        #         direction = 1.0
        #     else:
        #         direction = -1.0

        #     dv = Vec2d(30.0 * direction, 0.0)
        #     self.body.velocity = self.body.rotation_vector.cpvrotate(dv)

        space.step(dt)

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