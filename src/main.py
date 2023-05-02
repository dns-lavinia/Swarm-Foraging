import sys 
import random 

import pymunk
import pymunk.pygame_util
import pygame

from pymunk.vec2d import Vec2d

# Local imports
import constants

# Have the same results with every run of the simulation
random.seed(1)

def random_sign():
    return 1 if random.randint(0, 2) < 1 else -1


class SRobot: 
    MASS = 0.65  # kg
    RADIUS = 10  # cm

    def __init__(self, space, homebase_pos):
        # Spawn the robot in the vicinity of the home base
        x = homebase_pos[0] + random_sign() * random.randint(20, 40)
        y = homebase_pos[1] + random_sign() * random.randint(20, 40)

        # Create the body of the robot
        self.body = self.__add_robot_body(space, position=(x, y))

    
    # TODO: this function will be changed accordingly when RL will be added
    # source: https://github.com/viblo/pymunk/blob/master/pymunk/examples/tank.py 
    def update(self, space, dt, target_pos):
        """Update the position of the robot."""
        
        target_delta = target_pos - self.body.position 
        turn = self.body.rotation_vector.cpvunrotate(target_delta).angle
        self.body.angle = self.body.angle - turn

        # Drive the robot towards the target object
        if (target_pos - self.body.position).get_length_sqrd() < 30 ** 2:
            # If the robot is close enough to the target object, stop
            self.body.velocity = 0, 0
        else:
            if target_delta.dot(self.body.rotation_vector) > 0.0:
                direction = 1.0
            else:
                direction = -1.0

            dv = Vec2d(30.0 * direction, 0.0)
            self.body.velocity = self.body.rotation_vector.cpvrotate(dv)

        space.step(dt)


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


def main():   
    pygame.init()

    # Set the screen dimensions 
    screen = pygame.display.set_mode(constants.BOARD_SIZE)
    
    # Set the title of the simulation
    pygame.display.set_caption("Foraging in Swarm Robotics")
    clock = pygame.time.Clock()

    # Considering the screen variable above, the space would
    # occupy this whole screen and would have a dimension of 
    # 500cm x 500cm
    space = pymunk.Space()
    space.graivty = (0.0, 9.81)

    target = add_target(space)
    homebase = add_homebase(space)
    homebase_center = int(homebase.body.position.x) + 10, int(homebase.body.position.y)
    
    robots = []
    for _ in range(3):
        robots.append(SRobot(space, homebase.body.position))

    # Declare the optional attributes of the space
    draw_options = pymunk.pygame_util.DrawOptions(screen)

    # Simulation loop
    while True:
        # Finish the execution of the game when a key/button is pressed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                sys.exit(0)

        # Advance the simulation with one step
        space.step(1/constants.FPS) 
        
        # Make the background green
        screen.fill(constants.COLOR["artichoke"])

        # Draw area around the homebase
        pygame.draw.circle(surface=screen, 
                           color=constants.COLOR["carmine"], 
                           center=homebase_center, 
                           radius=25, 
                           width=1)

        space.debug_draw(draw_options)

        for i in range(3):
            robots[i].update(space, 1 / constants.FPS, target.body.position)

        pygame.display.flip()
        clock.tick(constants.FPS)


def add_target(space):
    """create and add to the space the target object that is to be carried by
    the robots to the home base."""

    mass = 1  # Mass in kg
    length = 20  # Length in cm

    body = pymunk.Body()

    # Spawn the robot in the lower right area
    x = random.randint(400, 420)
    y = random.randint(80, 120)

    # Set the initial position of the robot
    body.position = x, y 

    # Add a square shape for the robot
    shape = pymunk.Poly.create_box(body, (length, length), 0.0)
    shape.color = constants.COLOR["hunter-green"]
    shape.mass = mass 
    shape.friction = 1

    # Add the target object to the sapce
    space.add(body, shape)

    return shape


def add_homebase(space):
    """Create and add to the space the homebase flag"""

    flag_sizes = [(25, 0), (0, 7), (0, -7)]
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    
    x = random.randint(50, 80)
    y = random.randint(400, 420)

    body.position = x, y 
    
    shape = pymunk.Poly(body, flag_sizes)
    shape.color = constants.COLOR["auburn"]
    
    space.add(body, shape)
    return shape


if __name__ == "__main__":
    sys.exit(main())