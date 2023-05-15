import numpy as np

from keras.models import Sequential
from keras.layers import InputLayer
from keras.layers import Dense 

import cma

# action = the action the robot takes, meaning, the vrot, vtrans and scaling
# move the robot with the given action
# after the new action is decided by the nn, then I fit it and update state

# inputs of the nn: S = (obj_x, obj_y, goal_x, goal_y, f_r_rot, f_r_sca)

def get_reward():
    return

def agent_controller():
    return

def run_episodes():
    # The first argument is the initial solution for a population of 8 
    # the initial solution is the starting point of the individuals in population
    # 
    # The second argument is the initial standard deviation which is 0.1
    es = cma.CMAEvolutionStrategy(3 * [0], 0.1)
    n_episodes = 3 
    
    for i in range(n_episodes):
        state = env.reset()  # reset the environment 
        max_sim_steps = 700
        eps *= eps_decay_factor 
        done = False 

        # Run as long as the maximum simulation steps number is not reached and 
        # as long as the robots did not reach the goal with the target
        while not done:
            if np.random.random() < eps:
                action = np.random.randing(0, env.action_space.n)
            else:
                action = np.argmax(model.predict)

            # update done 


def main():
    model = Sequential()
    model.add(InputLayer(8))
    model.add(Dense(64, activation="tanh"))
    model.add(Dense(64, activation="tanh"))
    model.add(Dense(3)) # linear activation

    # Compile the model


if __name__ == "__main__":
    main()