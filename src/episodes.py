import math  # TODO: delete this later
import time
import sys
import os 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress tensorflow warnings

import numpy as np
import pygame

from keras.models import Sequential
from keras.layers import Dense

# Local imports 
import constants
import log

from sim import Simulation
from swarm import SwarmState


def create_nn():
    # NOTE: I changed the output of the neural network to 2 outputs instead of
    # 3, to represent vtras and vrot (I ignored the scaling part for now and
    # I assumed that the swarm is already in an optimal scaling from the beginning)
    model = Sequential()
    model.add(Dense(64, activation="tanh", input_shape=(6,)))
    model.add(Dense(64, activation="tanh"))
    model.add(Dense(2, activation="linear")) # linear activation

    # Compile the model
    model.compile(loss='mse', optimizer='adam')

    return model


def run_episodes():
    logger = log.create_logger(name="episodes",
                               level=log.LOG_DEBUG)
    
    logger.debug("Running all of the episodes.")

    # Initializing some constants but not only
    discount_factor = 0.95
    eps = 0.5
    eps_decay_factor = 0.999
    n_episodes = 4

    sim = Simulation()
    model = create_nn()

    # Get the position of the homebase to show it in the simulation
    goal_x, goal_y = sim.get_homebase_pos()

    logger.debug("Before the simulation loop.")
        
    ########################################################################
    # REINFORCEMENT LEARNING ALGO
    ########################################################################
    for _ in range(n_episodes):
        logger.debug("Episode started.")

        state = sim.reset()  # reset the environment 
        state = np.reshape(state, [1, len(state)])

        eps *= eps_decay_factor 
        done = False 
        sim_steps = constants.MAX_SIM_STEPS

        # Run as long as the maximum simulation steps number is not reached and 
        # as long as the robots did not reach the goal with the target
        while not done:
            print(f"Step {700 - sim_steps}")
            if np.random.random() < eps:
                # Get a random action
                action = np.random.randint(0, sim.ACTION_SPACE_N)
            else:
                action = np.argmax(model.predict(state))
            
            # Run the simulation with the given action
            new_state, reward, done = sim.step(action)
            new_state = np.reshape(new_state, [1, len(new_state)])

            logger.debug(f"The chosen action is {action}.")
            # logger.debug(f"State is {state}, and the new state is {new_state}")

            target = reward \
                    + discount_factor * np.max(model.predict(state))

            target_vector = model.predict(state)[0]
            target_vector[action] = target 

            # Train the model
            model.fit(
                state,
                target_vector.reshape(-1, sim.ACTION_SPACE_N),
                epochs=1, verbose=0
            )

            state = new_state

            # Update the remaining simulation steps
            sim_steps -= 1

            # Update done
            done = done | (sim_steps <= 0) 

            logger.debug("End of one iteration.")

            ####################################################################
            # Pygame dependent updates
            ####################################################################
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

            # # Draw the homebase flag                            
            # pygame.draw.polygon(surface=sim.screen, 
            #                     color=constants.COLOR["auburn"], 
            #                     points=((goal_x+25, goal_y),(goal_x, goal_y+7),(goal_x, goal_y-7)))

            sim.space.debug_draw(sim.draw_options)

            pygame.display.flip()

            # advance time
            sim.clock.tick(constants.FPS)

            # TODO: delete this later
            time.sleep(5)
            ####################################################################


def test_swarm_movement():
    sim = Simulation()
    goal_x, goal_y = sim.get_homebase_pos() 
    done=False
    
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

        # Rotate the swarm to the left
        if not done:
            new_state, reward, done = sim.step(0)

        # Wait until every robot gets into its position
        while sim.swarm.state != SwarmState.NONE:
            # Finish the execution of the game when a key/button is pressed
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    sys.exit(0)

            # Advance the simulation with one step
            sim.space.step(1/constants.FPS) 

            sim.swarm.run()

            # Make the background green
            sim.screen.fill(constants.COLOR["artichoke"])

            pygame.draw.circle(sim.screen, [0, 255, 0], center=sim.swarm.position, radius=sim.swarm.f_sca)

            sim.space.debug_draw(sim.draw_options)

            # Draw the homebase flag                            
            pygame.draw.polygon(surface=sim.screen, 
                                color=constants.COLOR["auburn"], 
                                points=((goal_x+25, goal_y),(goal_x, goal_y+7),(goal_x, goal_y-7)))
        
            pygame.display.flip()
            sim.clock.tick(constants.FPS)
        
        done=False

        pygame.draw.circle(sim.screen, [0, 255, 0], center=sim.swarm.position, radius=sim.swarm.f_sca)

        # Draw the homebase flag                            
        pygame.draw.polygon(surface=sim.screen, 
                            color=constants.COLOR["auburn"], 
                            points=((goal_x+25, goal_y),(goal_x, goal_y+7),(goal_x, goal_y-7)))
        # pygame.draw.circle(sim.screen, [0, 255, 0], center=sim.swarm.position, radius=sim.swarm.f_sca)

        # x_1 = sim.swarm.position[0] + sim.swarm.f_sca * math.cos(sim.swarm.angle + sim.swarm.U_SHAPE_ALPHA/2)
        # y_1 = sim.swarm.position[1] + sim.swarm.f_sca * math.sin(sim.swarm.angle + sim.swarm.U_SHAPE_ALPHA/2)
        # pygame.draw.circle(sim.screen, [0, 0, 255], center=(x_1, y_1), radius=1)

        # x_2 = sim.swarm.position[0] + sim.swarm.f_sca * math.cos(sim.swarm.angle - sim.swarm.U_SHAPE_ALPHA/2)
        # y_2 = sim.swarm.position[1] + sim.swarm.f_sca * math.sin(sim.swarm.angle - sim.swarm.U_SHAPE_ALPHA/2)
        # pygame.draw.circle(sim.screen, [0, 0, 255], center=(x_2, y_2), radius=1)

        sim.space.debug_draw(sim.draw_options)
        
        pygame.display.flip()
        sim.clock.tick(constants.FPS)


if __name__ == "__main__":
    # test_swarm_movement()
    run_episodes()