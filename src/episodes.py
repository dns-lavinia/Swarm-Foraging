import os 
import time
import json
import random
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress tensorflow warnings

from datetime import datetime
from keras.models import Sequential
from keras.layers import Dense, Flatten
from keras.optimizers import Adam

from rl.agents import SARSAAgent, DQNAgent
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


def run_random():
    """Run the simulation using random actions."""

    sim = Simulation()
    max_steps = 35000

    episode_reward = []
    nb_episode_steps = []
    nb_steps = []

    ep_reward = 0
    ep_steps = 0
    steps = 0

    start_time = time.time() 

    while steps < max_steps:
        # Generate the next random action 
        action = random.randint(0, 1)

        _, reward, done, _ = sim.step(action)

        ep_reward += reward
        ep_steps += 1
        steps += 1

        if done is True:
            episode_reward.append(ep_reward)
            nb_episode_steps.append(ep_steps)
            nb_steps.append(steps)

            ep_reward = 0
            ep_steps = 0

            sim.reset()
    
    end_time = time.time()
    print(f"Ran for {end_time-start_time}s")

    history = {
        "episode_reward": episode_reward,
        "nb_episode_steps": nb_episode_steps,
        "nb_steps": nb_steps,
    }

    dump_to_file(history, prefix="rnd")


def run_episodes_dqn(mode=None):
    """Run the simulation using the DQN RL method."""

    sim = Simulation()
    model = create_nn()

    memory = SequentialMemory(limit=50000, window_length=1)
    policy = BoltzmannQPolicy()
    
    dqn = DQNAgent(model=model,
                   nb_actions=sim.ACTION_SPACE_N,
                   memory=memory,
                   nb_steps_warmup=20,
                   target_model_update=1e-2,
                   policy=policy,
                   test_policy=policy)

    dqn.compile(Adam(learning_rate=3e-4), metrics=['mae'])
    
    if mode == "test":
        weights_filename = "data/dqn_weights_2023-06-01 16:44:28.838974.h5f"

        # load the weights
        dqn.load_weights(weights_filename)

        dqn.test(sim,
                 nb_episodes=5,
                 nb_max_episode_steps=constants.MAX_EP_STEPS)

        return 

    history = dqn.fit(sim, 
                      nb_steps=200000, 
                      verbose=2,
                      nb_max_episode_steps=constants.MAX_EP_STEPS)
    
    dump_to_file(history.history, prefix="dqn")

    # Save the weights 
    dqn.save_weights(f'models/dqn_weights_{datetime.today()}.h5f', overwrite=False)


def run_episodes_sarsa(mode=None):
    """Run the simulation using the SARSA RL method."""

    sim = Simulation()
    model = create_nn()
    

    policy = BoltzmannQPolicy()
    sarsa = SARSAAgent(model=model,
                       nb_actions=sim.ACTION_SPACE_N,
                       nb_steps_warmup=20,
                       policy=policy,
                       test_policy=policy)
    
    sarsa.compile(Adam(learning_rate=3e-4), metrics=['mae'])
    
    if mode == "test":
        weights_filename = "data/sarsa_weights_2023-06-21 14:18:26.608588.h5f"

        # load the weights
        sarsa.load_weights(weights_filename)

        history = sarsa.test(sim,
                             nb_episodes=100,
                             nb_max_episode_steps=constants.MAX_EP_STEPS)
        
        print(history.history)
        dump_to_file(history.history, prefix="sarsa-3")

        return 

    history = sarsa.fit(sim, 
                        nb_steps=200000, 
                        verbose=2,
                        nb_max_episode_steps=constants.MAX_EP_STEPS)
    
    dump_to_file(history.history, prefix="sarsa")

    # Save the weights 
    sarsa.save_weights(f'models/sarsa_weights_{datetime.today()}.h5f', overwrite=False)


def dump_to_file(data, prefix):
    with open(f'data/{prefix}_data{datetime.today()}.json', 'w') as f:
        json.dump(data, f, default=int)

if __name__ == "__main__":
    run_episodes_sarsa("test")