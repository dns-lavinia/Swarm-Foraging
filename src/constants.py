""" This module defines constants that are used throught the project. """

COLOR = {
    "artichoke": (143, 151, 121),
    "hunter-green": (53, 94, 59, 0),
    "grey": (110, 110, 110, 0),
    "auburn": (165, 42, 42),
    "carmine": (150, 0, 24),
    "black": (0, 0, 0, 0)
}

SCREEN_SIZE = (500, 500)

FPS = 60
ROBOTS_NUMBER = 3

MAX_SIM_STEPS = 400
SWARM_BOX_NEAR = 15
MIN_DIST_CHANGE = 1  # cm

TASK_TO_FOOD = 1
TASK_TO_NEST = 2

# The learning rate for the network
LR = 0.001