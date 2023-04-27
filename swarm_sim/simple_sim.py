import sys 
import random 

import pymunk
import pymunk.pygame_util
import pygame

# Have the same results with every run of the simulation
random.seed(1)


def main():   
    pygame.init()

    # Set the screen dimensions 
    screen = pygame.display.set_mode((600, 600))
    
    # Set the title of the simulation
    pygame.display.set_caption("Foraging in Swarm Robotics")
    clock = pygame.time.Clock()

    space = pymunk.Space()
    space.graivty = (0.0, 9.81)

    # Generate 3 robots
    robots = []
    for _ in range(3):
        srobot_shape = add_srobot(space)
        robots.append(srobot_shape)

    draw_options = pymunk.pygame_util.DrawOptions(screen)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                sys.exit(0)

        space.step(1/50.0)  # Advance simulation with one step
        
        # The screen shade is 'Artichoke'
        screen.fill((143, 151, 121))
        space.debug_draw(draw_options)

        pygame.display.flip()
        clock.tick(50)


def add_srobot(space):
    mass = 0.65  # Mass in kg
    radius = 10 # Radius in cm

    # Create the body of the robot
    body = pymunk.Body()
    x = random.randint(280, 320)  # Spawn the robot in the center area (nest)
    y = random.randint(280, 320) 

    # Set the initial position of the robot
    body.position = x, y 

    # Add a circular shape for the robot
    shape = pymunk.Circle(body, radius)
    shape.color = (72, 72, 72, 0)

    # Set the mass of the robot
    shape.mass = mass 

    shape.friction = 1  # The Friction value for dry concrete

    # Add the robot to the space
    space.add(body, shape)

    return shape


if __name__ == "__main__":
    sys.exit(main())