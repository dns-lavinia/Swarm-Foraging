import math

# Local imports
import constants

from srobot import SRobot


class SwarmController:
    # The space that has to be left empty in the swarm formation circle
    U_SHAPE_ALPHA = math.pi

    # The default size of the swarm.
    SWARM_SIZE = 3

    # The angle that the swarm has to change when given the action to rotate. 
    # The direction of the rotation has to be given by vrot.
    ROT_ANGLE = math.pi / 10

    def __init__(self, start_pos, start_angle, sim_space, goal_pos, *, swarm_size=SWARM_SIZE):
        self.space = sim_space
        self.goal_pos = goal_pos

        self.swarm_size = swarm_size
        self.position = start_pos
        self.angle = start_angle  # in radians
        self.f_sca = 20  # Denotes the radius of the swarm formation

        # Compute the beta angle (in radians)
        self.b_angle = (2 * math.pi - self.U_SHAPE_ALPHA) / (swarm_size - 1)

        # Add the robots in the swarm and place them in a U shape
        self.robots = self.__add_robots()

        # Flag used to denote that the swarm is busy
        self.in_motion = False

        self.r_target_pos = None
        self.state = "NONE"

    def perform_action(self, action):
        """Perform an action.
        
        Args:
            action (int): Can be one of the three options: 0 = tras, 1 = rot, 
            3 = sca.
        """
        
        assert (action in [0, 1, 2]), \
                "[Simulation.step] Given action is not recognized"

        # If the swarm is ready to accept commands  
        if self.state == "NONE":
            # Get the velocities to be used for the robots in the swarm
            vtras, vrot = self.get_avg_vel()

            # Move the swarm
            if action == 0:
                self.state = "IN_TRANSLATION"

            # Rotate the swarm
            elif action == 1:
                # Target positions for eac robot in the swarm
                self.r_target_pos = []

                # Start the translation movement for all of the robots to their
                # new designated position in the swarm
                for i in range(self.swarm_size):
                    # Get the new position of the robot within the swarm
                    new_pos = self.__compute_new_pos_for_robot(vrot, robot_n=i)
                    
                    # Save the new position
                    self.r_target_pos.append(new_pos)

                self.state = "IN_ROTATION_PART1"
        
        elif self.state == "IN_TRANSLATION":
            self.state = "NONE"
        
        elif self.state == "IN_ROTATION_PART1":
            finished_tras = 0

            # Move each robot to the new spot
            for i in range(self.swarm_size):
                dist = (self.robots[i].body.position - self.r_target_pos[i]).get_length_sqrd()

                if dist >= 0.5 ** 2:
                    self.robots[i].move_to(target_pos=self.r_target_pos[i])
                else:
                    self.robots[i].body.velocity = 0, 0
                    finished_tras += 1
                    
            # If all of the robots finished moving to their designated position
            # align them with the swarm angle
            if finished_tras == self.swarm_size:
                # Update the angle of the swarm
                self.angle = self.angle - self.ROT_ANGLE
                
                self.state="IN_ROTATION_PART2"

        elif self.state == "IN_ROTATION_PART2":
            finished_rot = 0

            for i in range(self.swarm_size):
                if ((self.robots[i].body.angle - self.angle) % (2 * math.pi)) > 0.1:
                    self.robots[i].rotate_to(self.angle)
                else: 
                    self.robots[i].body.angular_velocity = 0
                    finished_rot += 1

            if finished_rot == self.swarm_size:
                self.state = "NONE"

    def get_avg_vel(self):
        """
        Returns:
            (float, float): Average vrot and vtras for all robots.
        """
        
        sum_vtras = 0
        sum_vrot = 0
        n = len(self.robots)

        for i in range(len(self.robots)):
            vtras, vrot = self.robots[i].get_velocities()

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
            x_new = swarm_center[0] + 20 * math.cos(old_angle + self.ROT_ANGLE)
            y_new = swarm_center[1] + 20 * math.sin(old_angle + self.ROT_ANGLE)
        else:
            # Move anti-clockwise
            x_new = swarm_center[0] + 20 * math.cos(old_angle - self.ROT_ANGLE)
            y_new = swarm_center[1] + 20 * math.sin(old_angle - self.ROT_ANGLE)
        
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
