import math

from enum import Enum

# Local imports
import log 
import constants

from srobot import SRobot


class SwarmState(Enum):
    NONE = 0
    
    # States used for the rotation of the swarm
    ROTATION_MOVE = 1
    ROTATION_ROT = 2

    # States used for the translation of the swarm
    TRANSLATION_INI = 3
    TRANSLATION_STOP = 4


class SwarmController:
    # The space that has to be left empty in the swarm formation circle
    U_SHAPE_ALPHA = math.pi

    # The default size of the swarm.
    SWARM_SIZE = 3

    # The angle that the swarm has to change when given the action to rotate. 
    # The direction of the rotation has to be given by vrot.
    ROT_ANGLE = math.pi / 5

    SWARM_RADIUS = 20  # in cm

    def __init__(self, start_pos, start_angle, sim_space, goal_pos, target, *, swarm_size=SWARM_SIZE):
        # Create and save the logger for this class
        self.logger = log.create_logger(name=self.__class__.__name__,
                                        level=log.LOG_INFO)
        
        self.space = sim_space
        self.goal_pos = goal_pos
        self.target = target

        self.swarm_size = swarm_size
        self.position = start_pos
        self.angle = start_angle  # in radians
        self.f_sca = self.SWARM_RADIUS  # in cm

        # Compute the beta angle (in radians)
        self.b_angle = (2 * math.pi - self.U_SHAPE_ALPHA) / (swarm_size - 1)

        # Add the robots in the swarm and place them in a U shape
        self.robots = self.__add_robots()

        # Flag used to denote that the swarm is busy
        self.in_motion = False

        self.r_target_pos = None
        self.r_dir = None
        self.vtras, self.vrot = None, None

        # Upon initialization, the swarm isn't performing any action
        self.state = SwarmState.NONE

        # At first, the task is to get the swarm to go to the object
        self.task = 1

    async def run(self, action=None, task=None):
        """The main body that drives the swarm. Can give an optional argument 
        which denotes the action to take (move the swarm linearly, rotate the
        swarm or scale it). If the swarm is already processing an action it will
        continue to do so until it is completed.
        
        Args:
            action (int): Can be one of the three options: 0 = tras, 1 = rot, 
            3 = sca or None (in which case the argument can be skipped).
        """
        
        assert (action in [0, 1, 2] or action is None), \
                "[Simulation.step] Given action is not recognized"
        
        if task is not None:
            self.task = task

        # Print a message in the case there is a given action and the swarm is 
        # already processing something else
        if self.state != SwarmState.NONE and action is not None:
            self.logger.info("The swarm is already running a different action")
            return

        # If the swarm is ready to accept commands  
        if self.state == SwarmState.NONE:
            # Get the velocities to be used for the robots in the swarm
            self.vtras, self.vrot = self.get_avg_vel()

            # Move the swarm
            if action == 0:
                self.state = SwarmState.TRANSLATION_INI

            # Rotate the swarm
            elif action == 1:
                # Target positions for each robot in the swarm
                self.r_target_pos = []

                # Start the translation movement for all of the robots to their
                # new designated position in the swarm
                for i in range(self.swarm_size):
                    # Get the new position of the robot within the swarm
                    new_pos = self.__compute_new_pos_for_robot(self.vrot, robot_n=i)
                    
                    # Save the new position
                    self.r_target_pos.append(new_pos)

                    # Stop the motion of the robot
                    for i in range(self.swarm_size):
                        await self.robots[i].stop_move()
                    
                self.state = SwarmState.ROTATION_MOVE
        
        elif self.state == SwarmState.TRANSLATION_INI:
            for i in range(self.swarm_size):
                await self.robots[i].move(self.vtras)
            
            # Update the position of the swarm
            new_x = self.position[0] + self.vtras * (3/constants.FPS) * math.cos(self.angle)
            new_y = self.position[1] + self.vtras * (3/constants.FPS) * math.sin(self.angle)
            
            self.position = new_x, new_y

            # Movement finished
            self.state = SwarmState.TRANSLATION_STOP
        
        elif self.state == SwarmState.TRANSLATION_STOP:
            for i in range(self.swarm_size):
                await self.robots[i].stop_move()

            # Movement finished
            self.state = SwarmState.NONE

        elif self.state == SwarmState.ROTATION_MOVE:
            finished_tras = 0

            # Move each robot to the new spot
            for i in range(self.swarm_size):
                dist = (self.robots[i].body.position - self.r_target_pos[i]).get_length_sqrd()

                if dist >= 0.5 ** 2:
                    await self.robots[i].move_to(target_pos=self.r_target_pos[i])
                else:
                    await self.robots[i].stop_move()
                    finished_tras += 1
                    
            # If all of the robots finished moving to their designated position
            # align them with the swarm angle
            if finished_tras == self.swarm_size:
                # Update the angle of the swarm
                self.set_angle(new_angle=(self.angle 
                                          + self.get_sign(self.vrot) * self.ROT_ANGLE))
                
                # Save the optimal direction that each robot should rotate at
                self.r_dir = []
                for i in range(self.swarm_size):
                    norm_angle = self.angle % (2 * math.pi)
                    norm_robot_angle = self.robots[i].body.angle % (2 * math.pi)
                    diff = (norm_angle - norm_robot_angle) % (2 * math.pi)

                    self.r_dir.append(1 if diff < math.pi else -1)
        
                self.state = SwarmState.ROTATION_ROT

        elif self.state == SwarmState.ROTATION_ROT:
            finished_rot = 0

            for i in range(self.swarm_size):
                norm_angle = self.angle % (2 * math.pi)
                norm_robot_angle = self.robots[i].body.angle % (2 * math.pi)
                
                if abs(norm_robot_angle - norm_angle) > 0.1:
                    await self.robots[i].rotate_to(self.angle, self.r_dir[i])
                else: 
                    await self.robots[i].stop_move()
                    finished_rot += 1

            if finished_rot == self.swarm_size:
                self.state = SwarmState.NONE

    def set_task(self, task):
        assert (task == 1 or task == 2), f"The task {task} is not recongized"
        
        self.task = task

    def set_angle(self, new_angle):
        self.angle = new_angle

    def get_sign(self, num):
        """
        Returns:
            int: sign(num)
        """

        if num > 0:
            return 1
        elif num < 0:
            return -1 
        
        return 0

    def get_avg_vel(self):
        """
        Returns:
            (float, float): Average vrot and vtras for all robots.
        """
        
        sum_vtras = 0
        sum_vrot = 0
        n = self.swarm_size

        for i in range(n):
            vtras, vrot = self.robots[i].get_velocities(self.target.body.position, self.task)

            sum_vtras += vtras
            sum_vrot += vrot

        return sum_vtras/n, sum_vrot/n

    def __compute_new_pos_for_robot(self, vrot, robot_n):
        """Based on the direction of the rotational velocity, compute the new 
        coordinates for a robot within the swarm.

        The new position is computed knowing the position of the robot, as well
        as the angle that the swarm would rotate at (see `SwarmController.ROT_ANGLE`).

        Args:
            vrot (float): Rotational velocity. Can be either positive or negative.
            robot_n (int): The order of the robot in the swarm.

        Returns:
            (int, int): New position for the designated robot within the swarm
        """
        old_angle = self.angle + self.U_SHAPE_ALPHA / 2 + (robot_n * self.b_angle)
        swarm_center = self.position

        if vrot > 0:
            # Move clockwise
            x_new = swarm_center[0] + self.f_sca * math.cos(old_angle + self.ROT_ANGLE)
            y_new = swarm_center[1] + self.f_sca * math.sin(old_angle + self.ROT_ANGLE)
        else:
            # Move anti-clockwise
            x_new = swarm_center[0] + self.f_sca * math.cos(old_angle - self.ROT_ANGLE)
            y_new = swarm_center[1] + self.f_sca * math.sin(old_angle - self.ROT_ANGLE)
        
        return x_new, y_new

    def __add_robots(self):
        """Arrange the robots in a U shape around the starting position of the
        swarm."""
        
        robots = []
        for i in range(self.swarm_size):
            # Get the position of the robot in the formation
            pos = self.__get_robot_pos(angle=(i * self.b_angle))

            robots.append(SRobot(space=self.space, 
                                 start_pos=pos,
                                 start_angle=self.angle,
                                 goal_pos=self.goal_pos))
        
        return robots
    
    def __get_robot_pos(self, angle):
        """Return the position of a robot for a given beta angle."""
        pos_x = self.position[0]  \
                + self.f_sca * math.cos(self.angle + self.U_SHAPE_ALPHA/2 + angle)
        
        pos_y = self.position[1] \
                + self.f_sca * math.sin(self.angle + self.U_SHAPE_ALPHA/2 + angle)

        return pos_x, pos_y 
