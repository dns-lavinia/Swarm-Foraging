import asyncio
import datetime
import os 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress tensorflow warnings

import numpy as np
import matplotlib.pyplot as plt

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
    model = Sequential()
    model.add(Dense(64, activation="tanh", input_shape=(5,)))
    model.add(Dense(64, activation="tanh"))
    model.add(Dense(2, activation="linear")) # linear activation

    # Compile the model
    model.compile(loss='mse', optimizer='adam')

    return model


async def run_episodes():
    logger = log.create_logger(name="episodes",
                               level=log.LOG_DEBUG)

    # Initializing some constants but not only
    discount_factor = 0.95
    eps = 0.5
    eps_decay_factor = 0.999
    n_episodes = 10

    sim = Simulation()
    model = create_nn()

    returns = [0] * n_episodes
        
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
            sim.print_state_info(new_state)
            logger.debug(f"The current reward is {reward}")

            # Update return
            returns[ep] += reward

            new_state = np.reshape(new_state, [1, len(new_state)])

            target = reward \
                    + discount_factor * np.max(model.predict(state))

            target_vector = model.predict(state)[0]
            target_vector[action] = target 

            # Train the model
            model.fit(
                state,
                target_vector.reshape(-1, sim.ACTION_SPACE_N),
                epochs=1, verbose="auto"
            )

            state = new_state

            # Update the remaining simulation steps
            sim_steps -= 1

            # Update done
            done = done | (sim_steps <= 0) 

    ########################################################################
    # SAVE THE WEIGHTS + PROCESS DATA
    ########################################################################
    
    model.save(f"models/model{datetime.datetime.now()}.h5")
    x_returns = [i for i in range(n_episodes)]

    plt.bar(x_returns, returns)
    plt.savefig(f'figures/fig{datetime.datetime.now()}.png')


if __name__ == "__main__":
    asyncio.run(run_episodes())