import os 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import sys 
import random

import pygame

# Local imports
import constants

from sim import Simulation

# Have the same results with every run of the simulation
random.seed(1)



def main():   
    sim = Simulation()
    sim.reset()

    goal_x, goal_y = sim.get_homebase_pos()

    # Simulation loop
    while True:
        # Finish the execution of the game when a key/button is pressed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                sys.exit(0)

        # Advance the simulation with one step
        sim.space.step(1/constants.FPS) 

        # Make the background green
        sim.screen.fill(constants.COLOR["artichoke"])

        # Draw the homebase flag                            
        pygame.draw.polygon(surface=sim.screen, 
                            color=constants.COLOR["auburn"], 
                            points=((goal_x+25, goal_y),(goal_x, goal_y+7),(goal_x, goal_y-7)))

        sim.space.debug_draw(sim.draw_options)

        pygame.display.flip()
        sim.clock.tick(constants.FPS)


if __name__ == "__main__":
    sys.exit(main())