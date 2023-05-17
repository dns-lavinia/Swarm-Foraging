import math

# Local imports
from srobot import SRobot
from fuzzy import RobotFuzzySystem


class SwarmController:
    # The space that has to be left empty in the swarm formation cirlce
    U_SHAPE_ALPHA = (math.pi / 5) * 2
    SWARM_SIZE = 3

    def __init__(self, start_pos, start_angle, sim_space, *, swarm_size=SWARM_SIZE):
        self.space = sim_space

        self.swarm_size = swarm_size
        self.position = start_pos
        self.angle = start_angle  # in radians
        self.f_sca = 20  # Denotes the radius of the swarm formation

        # Compute the beta angle (in radians)
        self.b_angle = (2 * math.pi - self.U_SHAPE_ALPHA) / swarm_size

        # Add the robots in the swarm and place them in a U shape
        self.robots = self.__add_robots()

    def perform_action(self, action):
        """Perform an action.
        
        Args:
            action (str): Can be one of the three options: `'tras'`, `'rot'`, `'sca'`.
        """
        
        assert (action == "tras" or action == "rot" or action == "sca"), \
                "[Simulation.step] Given action is not recognized"
        
        # Get the average translational and rotational speed of the robots
        sum_vtras = 0
        sum_vrot = 0

        # for i in range(len(self.robots)):
        #     vtras, vrot = self.robots[i].
        
        if action == "tras":
            # Move the swarm
            pass
            
        elif action == "rot":
            # Rotate the swarm
            pass 

        elif action == "sca":
            # Scale the swarm
            pass 
        

    def __add_robots(self):
        # Around the starting position, arrange the robots in a U shape
        robots = []
        for i in range(self.swarm_size):
            # Get the position of the robot in the formation
            pos = self.__get_robot_pos(angle=(i * self.b_angle))

            robots.append(SRobot(self.space, start_pos=pos))
        
        return robots
    
    def __get_robot_pos(self, angle):
        """Return the position of a robot for a given beta angle."""
        pos_x = self.position[0]  \
                + self.f_sca * math.cos(self.angle - self.U_SHAPE_ALPHA/2 - angle)
        
        pos_y = self.position[1] \
                + self.f_sca * math.sin(self.angle - self.U_SHAPE_ALPHA/2 - angle)

        return pos_x, pos_y 