import os 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import sys

import numpy as np
import pygame
import keras

from keras.models import Sequential
from keras.layers import Dense, InputLayer

# Local imports 
import constants

from sim import Simulation

# action = the action the robot takes, meaning, the vrot, vtrans and scaling
# move the robot with the given action
# after the new action is decided by the nn, then I fit it and update state

# inputs of the nn: S = (obj_x, obj_y, goal_x, goal_y, f_r_rot, f_r_sca)

def create_nn():
    print("Creating neural network")

    model = Sequential()
    model.add(Dense(64, activation="tanh", input_shape=(6,)))
    model.add(Dense(64, activation="tanh"))
    model.add(Dense(3, activation="linear")) # linear activation

    # Compile the model
    model.compile(loss='mse', optimizer='adam')

    return model


def run_episodes():
    print("Running all of the episodes")

    discount_factor = 0.95
    eps = 0.5
    eps_decay_factor = 0.999
    n_episodes = 4

    sim = Simulation()
    model = create_nn()

    goal_x, goal_y = sim.get_homebase_pos()

    print("Before the simulation loop")
        
    ########################################################################
    # REINFORCEMENT LEARNING ALGO
    ########################################################################
    for _ in range(n_episodes):
        print("Started new episode")

        state = sim.reset()  # reset the environment 
        state = np.reshape(state, [1, len(state)])

        eps *= eps_decay_factor 
        done = False 
        sim_steps = constants.MAX_SIM_STEPS

        # Run as long as the maximum simulation steps number is not reached and 
        # as long as the robots did not reach the goal with the target
        while not done:
            if np.random.random() < eps:
                # Get a random action
                action = np.random.randint(0, sim.ACTION_SPACE_N)
            else:
                action = np.argmax(model.predict(state))
            
            print("Chosen action ", action)
            
            new_state, reward, done = sim.step(action)

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

            new_state = np.reshape(new_state, [1, len(new_state)])
            state = new_state

            # Update the remaining simulation steps
            sim_steps -= 1

            # Update done
            print("Done is", done)
            done = done | (sim_steps <= 0) 

            print("Everything was computed for one iteration")

            ################################################################
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
            ################################################################

            # advance time
            sim.clock.tick(constants.FPS)
    
    ########################################################################


if __name__ == "__main__":
    run_episodes()