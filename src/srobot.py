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
    logger =  log.create_logger(name="Robot",
                                level=log.LOG_DEBUG)

    def __init__(self, space, start_pos, start_angle, goal_pos):
        # Save the space the robots are going to be placed in
        self.space = space

        # All of the robots know the goal or the nest position
        self.goal_pos = goal_pos

        # Create the body of the robot
        self.body = self.__add_robot_body(space, 
                                          position=start_pos, 
                                          start_angle=start_angle)

        # Attach a LaserSensor to it
        self.sensor = LaserSensor(position=start_pos, body_angle=self.body.angle,
                                  n_readings=32, start_angle=-90,
                                  angle_space=6, range=400)

        # Attach the fuzzy controller to it
        self.flc = RobotFuzzySystem()
    
    async def move(self, vtras):
        self.space.step(1/constants.FPS)

        dv = Vec2d(vtras, 0.0)
        self.body.velocity = self.body.rotation_vector.cpvrotate(dv)

        # Update the position of the sensor
        self.sensor.update_position(self.body.position, self.body.angle)

    async def stop_move(self):
        # Reset the velocity
        self.body.velocity = 0, 0

        # Reset the angular velocity
        self.body.angular_velocity = 0

        self.space.step(1/constants.FPS)

        # Update the position of the sensor
        self.sensor.update_position(self.body.position, self.body.angle)
    
    async def move_to(self, target_pos):
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

    async def rotate_to(self, angle, direction):
        """Rotate the robot to a given angle."""

        norm_angle = angle % (2 * math.pi)
        norm_self_angle = self.body.angle % (2 * math.pi)

        if norm_angle < 0:
            norm_angle = 2 * math.pi - norm_angle
        
        if norm_self_angle < 0:
            norm_self_angle = 2 * math.pi - norm_self_angle

        if abs(norm_self_angle - norm_angle) < 0.1:
            self.body.angular_velocity = 0
        else:
            self.body.angular_velocity = direction * math.pi/3

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
        shape.body.damping = 0.99
        shape.color = constants.COLOR["grey"]

        # Add the body to the space
        space.add(body, shape)

        return body
    
    def get_velocities(self, target_pos, task=1):
        """
        Args:
            task (int): The task to be considered by FLC. Can be either 1 or 2.
            If task == 1, then then the target is considered to be the food 
            object. If task == 2, then the target is considered to be the home
            base.

        Returns:
            (float, float): Returns translational and roational velocities (in
            this order) once they are computed by the FLC.
        """

        assert (task == 1 or task == 2), "Task not recongized"

        if task == 1:
            distances = self.sensor.get_reading(obj_color=constants.COLOR["hunter-green"][:3])
        elif task == 2:
            distances = self.sensor.get_reading(obj_color=constants.COLOR["auburn"])

        n = len(distances)

        # Get the minimum distance for readings of the left zone
        left_dist = min(distances[0 : (n // 3)])

        # Get the minimum distance for readings of the front zone
        front_dist = min(distances[(n // 3) : (2 * n // 3 + n%3)])

        # Get the minimum distance for readings of the right zone
        right_dist = min(distances[(2 * n // 3 + n%3) : n])

        # Compute the distance to goal from the target object 
        dist = math.sqrt((self.body.position[0] - target_pos[0]) ** 2  
                         + (self.body.position[1] - target_pos[1]) ** 2)
        
        # Compute the angle of the target object to the goal
        # The value should be between -pi and pi
        angle_to_goal = self.body.angle - math.atan2(target_pos[1] - self.body.position[1],
                                                     target_pos[0] - self.body.position[0])

        # Normalize the angle 
        angle_to_goal = self.__normalize_angle(angle_to_goal)

        # Save the new velocities
        vtras, vrot = self.flc.evaluate(inp_left=left_dist,
                                        inp_front=front_dist,
                                        inp_right=right_dist,
                                        inp_ang=angle_to_goal,
                                        inp_dist=dist)
        
        self.logger.debug(f'Readings for the FLC: {[left_dist, front_dist, right_dist, angle_to_goal, dist]}')
        self.logger.debug(f'New velocities: vtras = {vtras}, vrot = {vrot}')

        return vtras, vrot
    
    def __normalize_angle(self, angle):
        angle = angle % (2 * math.pi)  # It is always a positive number

        if angle > math.pi:
            return -1 * (2 * math.pi - angle)
    
        return angle