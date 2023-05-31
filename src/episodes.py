import datetime
import asyncio
import time
import json
import os 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress tensorflow warnings

import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np

from keras.models import Sequential
from keras.layers import Dense

# Local imports 
import constants
import log

from sim import Simulation


def create_nn():
    # NOTE: I changed the output of the neural network to 2 outputs instead of
    # 3, to represent vtras and vrot (I ignored the scaling part for now and
    # I assumed that the swarm is already in an optimal scaling from the beginning)

    init = tf.keras.initializers.HeUniform()
    model = Sequential()
    model.add(Dense(64, activation="relu", input_shape=(5,), kernel_initializer=init))
    model.add(Dense(64, activation="relu"))
    model.add(Dense(2, activation="linear")) # linear activation

    # Compile the model
    optimizer = tf.keras.optimizers.Adam(lr=constants.LR)
    model.compile(loss=tf.keras.losses.Huber(), optimizer=optimizer, metrics=['accuracy'])

    return model


async def run_episodes():
    logger = log.create_logger(name="episodes",
                               level=log.LOG_INFO)

    # Initializing some constants but not only
    discount_factor = 0.95
    eps = 0.5
    eps_decay_factor = 0.999
    n_episodes = 20

    sim = Simulation()
    model = create_nn()

    rewards_per_step = []
    rewards_per_ep = [0] * n_episodes
    timesteps_per_ep = [0] * n_episodes
    total_reward = 0

    start_time = time.time()
        
    ########################################################################
    # REINFORCEMENT LEARNING ALGO
    ########################################################################
    for ep in range(n_episodes):
        state = sim.reset()  # reset the environment 
        state = np.reshape(state, [1, len(state)])

        eps *= eps_decay_factor 
        done = False 
        sim_steps = constants.MAX_SIM_STEPS

        # Run as long as the maximum simulation steps number is not reached and 
        # as long as the robots did not reach the goal with the target
        while not done:
            logger.info(f"STEP [{constants.MAX_SIM_STEPS - sim_steps}]")

            if np.random.random() < eps:
                # Get a random action
                action = np.random.randint(0, sim.ACTION_SPACE_N)
            else:
                action = np.argmax(model.predict(state))
            
            # Run the simulation with the given action
            new_state, reward, done = await sim.step(action)

            logger.debug(f"[CURRENT ACTION: {action}]")
            # sim.print_state_info(new_state)
            logger.debug(f"The current reward is {reward}")

            new_state = np.reshape(new_state, [1, len(new_state)])

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

            # Update the timestep
            total_reward += reward
            rewards_per_step.append(total_reward)
            rewards_per_ep[ep] += reward
            timesteps_per_ep[ep] += 1

            # Update done
            done = done | (sim_steps <= 0) 

    ########################################################################
    # SAVE THE WEIGHTS + PROCESS DATA
    ########################################################################
    
    # Save the model
    model.save(f"models/model{datetime.datetime.now()}.h5")

    # Save the metrics for this RL algo run
    data = {
        'rewards_per_step': rewards_per_step,
        'reward_per_ep': rewards_per_ep,
        'timesteps_per_ep' : timesteps_per_ep,
        'total_time': time.time()-start_time,
    }

    filename = f'data/data{datetime.datetime.now()}.json'
    with open(filename, 'w') as fp:
        json.dump(data, fp)
    

if __name__ == "__main__":
    asyncio.run(run_episodes())