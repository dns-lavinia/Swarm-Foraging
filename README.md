## Overview

The current project is intended to be used as part of the Bachelor Thesis. 

For this, I chose to bring my own implementation of a swarm robotics system that
uses collaboration in a foraging task.

## Installing the needed packages
Before running the project, all the needed python packages have to be installed.

If they are not already, simply run `pip install requirements.txt` from a terminal 
from the folder the file `requirements.txt` is from.

It should be noted that for the _keras_ library some additional packages may be
needed. To install all of the needed dependencies [this](https://www.tutorialspoint.com/keras/keras_installation.htm) tutorial can be followed.  

## Running the simulation

There are two main ways in which the simulation can be run: either start the
learning process from zero, or load the weights of the already trained models
used for the SARSA and DQN reinforcement learning algorithms.

The Python file `episodes.py` is the main file in this project that runs the
simulation. By default, the weights of the trained model used for the SARSA
algorithm is loaded, with the function call `run_episodes_sarsa("test")`. If
no argument is given to this function call (`run_episodes_sarsa()`), then the learning process starts from zero.

There are two additional functions in `episodes.py`, one function that can be used
for the DQN reinforcement learning algorithm that can be called in a similar way
as to the function described above, either in testing mode (`run_episodes_dqn("test")`)
or not (`run_episodes_dqn()`). The other function (`run_random()`) can be used to run the simulation using randomly generated actions to be employed by the swarm.