import math  # TODO: delete this later
import time
import random
import sys
import asyncio
import os 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress tensorflow warnings

import numpy as np
import pygame

from keras.models import Sequential
from keras.layers import Dense
from collections import deque

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
    model.add(Dense(64, activation="tanh", input_shape=(5,)))
    model.add(Dense(64, activation="tanh"))
    model.add(Dense(2, activation="linear")) # linear activation

    # Compile the model
    model.compile(loss='mse', optimizer='adam')

    return model

# Source: https://github.com/PacktPublishing/Deep-Reinforcement-Learning-with-Python/
class DQN:
    def __init__(self, state_size, action_size):
        
        #define the state size
        self.state_size = state_size
        
        #define the action size
        self.action_size = action_size
        
        #define the replay buffer
        self.replay_buffer = deque(maxlen=5000)
        
        #define the discount factor
        self.gamma = 0.9  
        
        #define the epsilon value
        self.epsilon = 0.8   
        
        #define the update rate at which we want to update the target network
        self.update_rate = 1000    
        
        #define the main network
        self.main_network = self.build_network()
        
        #define the target network
        self.target_network = self.build_network()
        
        #copy the weights of the main network to the target network
        self.target_network.set_weights(self.main_network.get_weights())
        
    def build_network(self):
        model = Sequential()
        model.add(Dense(64, activation="tanh", input_shape=(5,)))
        model.add(Dense(64, activation="tanh"))
        model.add(Dense(2, activation="linear")) # linear activation

        # Compile the model
        model.compile(loss='mse', optimizer='adam')

        return model

    #We learned that we train DQN by randomly sampling a minibatch of transitions from the
    #replay buffer. So, we define a function called store_transition which stores the transition information
    #into the replay buffer

    def store_transistion(self, state, action, reward, next_state, done):
        self.replay_buffer.append((state, action, reward, next_state, done))
        
    #We learned that in DQN, to take care of exploration-exploitation trade off, we select action
    #using the epsilon-greedy policy. So, now we define the function called epsilon_greedy
    #for selecting action using the epsilon-greedy policy.
    
    def epsilon_greedy(self, state):
        if random.uniform(0,1) < self.epsilon:
            return np.random.randint(self.action_size)
        
        Q_values = self.main_network.predict(state)
        
        return np.argmax(Q_values[0])

    #train the network
    def train(self, batch_size):
        
        #sample a mini batch of transition from the replay buffer
        minibatch = random.sample(self.replay_buffer, batch_size)
        
        #compute the Q value using the target network
        for state, action, reward, next_state, done in minibatch:
            if not done:
                target_Q = (reward + self.gamma * np.amax(self.target_network.predict(next_state)))
            else:
                target_Q = reward
                
            #compute the Q value using the main network 
            Q_values = self.main_network.predict(state)
            
            Q_values[0][action] = target_Q
            
            #train the main network
            self.main_network.fit(state, Q_values, epochs=1, verbose=0)
            
    #update the target network weights by copying from the main network
    def update_target_network(self):
        self.target_network.set_weights(self.main_network.get_weights())

# Source: https://github.com/PacktPublishing/Deep-Reinforcement-Learning-with-Python/
async def run_episodes_enhanced():
    num_episodes = 24
    num_timesteps = 700
    batch_size = 8
    num_screens = 4 

    sim = Simulation()

    dqn = DQN(sim.OBSERVATION_SPACE_N, sim.ACTION_SPACE_N)

    done = False 
    time_step = 0

    #for each episode
    for i in range(num_episodes):
        
        #set return to 0
        Return = 0
        
        #preprocess the game screen
        state = sim.reset()
        state = np.reshape(state, [1, len(state)])

        #for each step in the episode
        for t in range(num_timesteps):
            #update the time step
            time_step += 1
            
            #update the target network
            if time_step % dqn.update_rate == 0:
                dqn.update_target_network()
            
            #select the action
            action = dqn.epsilon_greedy(state)
            
            #perform the selected action
            next_state, reward, done = await sim.step(action)
            next_state = np.reshape(next_state, [1, len(next_state)])
            
            #store the transition information
            dqn.store_transistion(state, action, reward, next_state, done)
            
            #update current state to next state
            state = next_state
            
            #update the return
            Return += reward
            
            #if the episode is done then print the return
            if done:
                print('Episode: ',i, ',' 'Return', Return)
                break
                
            #if the number of transistions in the replay buffer is greater than batch size
            #then train the network
            if len(dqn.replay_buffer) > batch_size:
                dqn.train(batch_size)

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

    # Get the position of the homebase to show it in the simulation
    goal_x, goal_y = sim.get_homebase_pos()
        
    ########################################################################
    # REINFORCEMENT LEARNING ALGO
    ########################################################################
    for _ in range(n_episodes):
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
            
            logger.debug(f"[CURRENT ACTION: {action}]")

            # Run the simulation with the given action
            new_state, reward, done = await sim.step(action)

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

            # Update done
            done = done | (sim_steps <= 0) 

if __name__ == "__main__":
    asyncio.run(run_episodes())
    # asyncio.run(run_episodes_enhanced())