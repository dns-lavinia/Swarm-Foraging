import random

import pygame
import pymunk
import pymunk.pygame_util

# Local imports
import constants

from srobot import SRobot


class Simulation:
    def __init__(self, screen_size=constants.SCREEN_SIZE):
        """Initialize the simulation.

        Args:
            screen_size ((int, int), optional): The size of the surface. Defaults 
            to constants.SCREEN_SIZE.
        """
        # Initialize the game
        pygame.init()

        # Save the dimension of the surface
        self.screen_size = screen_size

        # Set the screen dimensions
        self.screen = pygame.display.set_mode(self.screen_size)

        # Set the title of the simulation
        pygame.display.set_caption("Foraging in Swarm Robotics")
        self.clock = pygame.time.Clock()

        # Considering the screen variable above, the space would occupy
        # this whole screen and would have a dimension equal to the one
        # specified above
        self.space = pymunk.Space()
        self.space.gravity = (0.0, 0.0)
    
        # Declare the optional attributes of the space
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
    
    def add_robots(self, start_pos, n_robots=constants.ROBOTS_NUMBER):
        """Add a number of robots to the simulation.

        Args:
            start_pos ((int, int)): The robots will be created around this 
            starting position.

            n_robots (int, optional): The number of robots to be created. 
            Defaults to constants.ROBOTS_NUMBER.

        Returns:
            A list containing the robots instances.
        """
    
        robots = []
        for _ in range(n_robots):
            robots.append(SRobot(self.space, start_pos))
        
        return robots

    def add_target(self, mass=1, length=20, position=None):
        """Create and add to the space of the simulation the target object that
        is to be carried by the robots to the home base. The shape of the target
        object will be a square.

        The mass is measured in kg.
        The length of the rectangular body is measured in cm.
        
        The target object will be added at the top right corner of the surface
        if the position is not specified."""

        body = pymunk.Body()

        # Add the target object in the upper right corner 
        # if the position is not given
        if position is None:
            h, w = self.screen_size
            x = random.randint(w - w/5, w - (w/5 - w/25))  # 400, 420
            y = random.randint(w/5 - w/25, w/5 + w/25)  # 80, 120
        else:
            x, y = position

        # Set the initial position of the target
        body.position = x, y

        # Add a square shape for the target
        shape = pymunk.Poly.create_box(body, (length, length), 0.0)
        shape.color = constants.COLOR["hunter-green"]
        shape.mass = mass  # mass in kg
        shape.friction = 1  

        # Add the target object to the space
        self.space.add(body, shape)

        return shape
    
    def add_homebase(self, position=None):
        """Create and add to the space the homebase flag.
        
        The homebase will be added at the bottom left corner of the surface if
        the position is not specified."""

        flag_sizes = [(25, 0), (0, 7), (0, -7)]
        body = pymunk.Body(body_type=pymunk.Body.STATIC)

        # Add the hombase in the lower left corner 
        # if the position is not given
        if position is None:
            h, w = self.screen_size
            x = random.randint(w/10, w/5 - w/25)  # 50, 80
            y = random.randint(w - w/5, w - (w/5 - w/25))  # 400, 420
        else:
            x, y = position

        body.position = x, y 
        
        shape = pymunk.Poly(body, flag_sizes)
        shape.color = constants.COLOR["auburn"]
        
        self.space.add(body, shape)
        return shape
