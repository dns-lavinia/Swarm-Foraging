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

        # Add a box around the environment so that objects cannot move past the
        # visible screen
        self.__add_boundary()
    
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
    
    def get_homebase_pos(self, position=None):
        """Returns the coordonates of the homebase (x, y)."""

        # Add the hombase in the lower left corner 
        # if the position is not given
        if position is None:
            h, w = self.screen_size
            x = random.randint(w/10, w/5 - w/25)  # 50, 80
            y = random.randint(w - w/5, w - (w/5 - w/25))  # 400, 420
        else:
            x, y = position

        return x, y

    def __add_boundary(self, color=constants.COLOR["black"]):
        """Initialize and add to the simulation a boundary around the visible
        environment.
        
        Args:
            color ((int, int, int, int)): The color of the boundary box.
        """

        static_body = self.space.static_body
        max_w, max_h = self.screen_size

        left_segm = pymunk.Segment(static_body, a=(0, 0), b=(0, max_h), radius=1.0)
        self.space.add(left_segm)
        left_segm.friction = 1
        left_segm.color = color

        right_segm = pymunk.Segment(static_body, a=(max_w-2, 0), b=(max_w-2, max_h-2), radius=1.0)
        self.space.add(right_segm)
        right_segm.friction = 1
        right_segm.color = color

        up_semg = pymunk.Segment(static_body, a=(0, 0), b=(max_w, 0), radius=1.0)
        self.space.add(up_semg)
        up_semg.friction = 1
        up_semg.color = color

        down_segm = pymunk.Segment(static_body, a=(0, max_h-2), b=(max_w-2, max_h-2), radius=1.0)
        self.space.add(down_segm)
        down_segm.friction = 1
        down_segm.color = color
