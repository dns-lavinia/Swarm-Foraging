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

    target = sim.add_target()
    homebase = sim.add_homebase()
    robots = sim.add_robots(start_pos=homebase.body.position)

    # Save the center of the homebase to draw a circle around this area
    homebase_center = int(homebase.body.position.x) + 10, int(homebase.body.position.y)

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

        # Draw area around the homebase
        pygame.draw.circle(surface=sim.screen, 
                           color=constants.COLOR["carmine"], 
                           center=homebase_center, 
                           radius=25, 
                           width=1)

        sim.space.debug_draw(sim.draw_options)

        for i in range(constants.ROBOTS_NUMBER):
            robots[i].update(sim.space, 1 / constants.FPS, target.body.position)
            robots[i].sensor.draw_sensor_angles()

        pygame.display.flip()
        sim.clock.tick(constants.FPS)


if __name__ == "__main__":
    sys.exit(main())