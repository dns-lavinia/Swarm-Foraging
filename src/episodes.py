import os 
import json
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress tensorflow warnings

from datetime import datetime
from keras.models import Sequential
from keras.layers import Dense, Flatten
from keras.optimizers import Adam

from rl.agents import SARSAAgent
from rl.policy import BoltzmannQPolicy

import cma

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


def run_episodes(mode=None):
    sim = Simulation()
    model = create_nn()

    policy = BoltzmannQPolicy()
    dqn = SARSAAgent(model=model,
                     nb_actions=sim.ACTION_SPACE_N,
                     nb_steps_warmup=10,
                     policy=policy)
    
    dqn.compile(Adam(learning_rate=3e-4), metrics=['mae'])
    
    if mode == "test":
        weights_filename = f'models/dqn_weights_2023-06-01 16:44:28.838974.h5f'

        # load the weights
        dqn.load_weights(weights_filename)
        dqn.fit(sim, nb_steps=1000, nb_max_episode_steps=constants.MAX_EP_STEPS)
        # dqn.test(sim, 
        #          nb_episodes=5,
        #          nb_max_episode_steps=constants.MAX_SIM_STEPS)

        return 

    history = dqn.fit(sim, 
                      nb_steps=50000, 
                      verbose=2,
                      nb_max_episode_steps=constants.MAX_EP_STEPS)
    
    print('[TESTING PHASE]')

    dqn.test(sim, 
             nb_episodes=5,
             nb_max_episode_steps=constants.MAX_EP_STEPS)
    
    print(history.history)
    dump_to_file(history.history)

    # Save the weights 
    dqn.save_weights(f'models/dqn_weights_{datetime.today()}.h5f', overwrite=False)


def dump_to_file(data):
    with open(f'data/data{datetime.today()}.json', 'w') as f:
        json.dump(data, f, default=int)

if __name__ == "__main__":
    run_episodes("test")