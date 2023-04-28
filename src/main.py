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

class SRobot: 
    MASS = 0.65  # kg
    RADIUS = 10  # cm

    def __init__(self, space, homebase_pos):
        # Create a control body that will be used together with the main body
        # to add motion to the robot
        self.control_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)

        # Spawn the robot in the vicinity of the home base
        # TODO: randomly generate the position for multiple robots
        x = homebase_pos[0] + 25
        y = homebase_pos[1] + 25

        self.control_body.position = x, y

        space.add(self.control_body)

        # Create the normal body
        self.body = self.__add_robot_body(space, position=(x, y))
        
        # Create the pivot element
        self.pivot = pymunk.PivotJoint(self.control_body, self.body, (0, 0), (0, 0))
        
        # Add the pivot element to the space
        space.add(self.pivot)
        self.pivot.max_bias = 0  # disable joint correction
        self.pivot.max_force = 10000  # emulate linear friction

        # Create the gear element
        self.gear = pymunk.GearJoint(self.control_body, self.body, 0.0, 1.0)
        
        # Add the gear element to the space
        space.add(self.gear)
        self.gear.error_bias = 0  # attempt to fully correct the joint each step
        self.gear.max_bias = 1.2  # but limit it's angular correction rate
        self.gear.max_force = 50000  # emulate angular friction

    
    # TODO: this function will be changed accordingly when the RL will be added
    # source: https://github.com/viblo/pymunk/blob/master/pymunk/examples/tank.py 
    def update(self, space, dt, target_pos):
        """Update the position of the robot."""
        
        target_delta = target_pos - self.body.position 
        turn = self.body.rotation_vector.cpvunrotate(target_delta).angle
        self.control_body.angle = self.body.angle - turn 

        # Drive the robot towards the target object
        if (target_pos - self.body.position).get_length_sqrd() < 30 ** 2:
            # If the robot is close enough to the target object, stop
            self.control_body.velocity = 0, 0
        else:
            if target_delta.dot(self.body.rotation_vector) > 0.0:
                direction = 1.0
            else:
                direction = -1.0

            dv = Vec2d(30.0 * direction, 0.0)
            self.control_body.velocity = self.body.rotation_vector.cpvrotate(dv)

        space.step(dt)


    def __add_robot_body(self, space, position):
        """Create and add to the space a box shape for the robot body
        
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
    robot = SRobot(space, homebase.body.position)

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
        robot.update(space, 1 / constants.FPS, target.body.position)

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