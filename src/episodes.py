import os 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress tensorflow warnings

from datetime import datetime

import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, Flatten
from keras.optimizers import Adam

from rl.agents.dqn import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory

# Local imports 
import constants

from sim import Simulation


def create_nn():
    # NOTE: I changed the output of the neural network to 2 outputs instead of
    # 3, to represent vtras and vrot (I ignored the scaling part for now and
    # I assumed that the swarm is already in an optimal scaling from the beginning)

    model = Sequential()
    model.add(Flatten(input_shape=(1, Simulation.OBSERVATION_SPACE_N,)))
    model.add(Dense(64, activation="tanh"))
    model.add(Dense(64, activation="tanh"))
    model.add(Dense(2, activation="linear")) # linear activation

    return model


def run_episodes():
    sim = Simulation()
    model = create_nn()

    memory = SequentialMemory(limit=50000, window_length=1)
    policy = BoltzmannQPolicy()
    dqn = DQNAgent(model=model,
                   nb_actions=sim.ACTION_SPACE_N,
                   memory=memory,
                   nb_steps_warmup=10,
                   target_model_update=1e-2,
                   policy=policy)
    
    dqn.compile(Adam(learning_rate=1e-3), metrics=['mae'])

    dqn.fit(sim, 
            nb_steps=8000, 
            visualize=True, 
            verbose=2, 
            nb_max_episode_steps=constants.MAX_SIM_STEPS)
    
    print('[TESTING PHASE]')

    dqn.test(sim, 
             nb_episodes=5, 
             nb_max_episode_steps=constants.MAX_SIM_STEPS, 
             visualize=True)

    # Save the weights 
    dqn.save_weights(f'models/dqn_weights_{datetime.today()}.h5f', overwrite=False)

if __name__ == "__main__":
    run_episodes()