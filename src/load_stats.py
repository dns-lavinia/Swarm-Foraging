import os
import json

import matplotlib.pyplot as plt

from dotenv import load_dotenv

# Load the env variables
load_dotenv()

def load_one(json_file_name):
    """
    Plot the accumulated reward for all of the episodes and the number of 
    steps per epsiode.
    """

    with open(json_file_name) as json_file:
        data = json.load(json_file)
        x = [(i+1) for i in range(len(data['episode_reward']))]

        total_reward = []
        sum = 0
        for reward in data['episode_reward']:
            sum += reward 
            total_reward.append(sum)

        plt.figure(1)
        plt.plot(x, total_reward)
        plt.xlabel('Episode number')
        plt.ylabel('Accumulated reward')

        plt.figure(2)
        plt.plot(x, data['nb_episode_steps'])
        plt.xlabel('Episode number')
        plt.ylabel('Number steps per episode')
        plt.show()


def load_200():
    """
    Load the learning data for the foraging task when using the DQN and the 
    deep SARSA RL algorithms.

    Plot the reward per epsiode and the number of steps per episode.
    """

    json_dqn = str(os.getenv("JSON_DQN_200K"))
    json_srs = str(os.getenv("JSON_SRS_200K"))

    with open(json_dqn) as json_file:
        data_dqn = json.load(json_file)

    with open(json_srs) as json_file:
        data_srs = json.load(json_file)

    x_dqn = [(i+1) for i in range(len(data_dqn['episode_reward']))]
    x_srs = [(i+1) for i in range(len(data_srs['episode_reward']))]

    total_reward_dqn = []
    sum_dqn = 0
    for reward in data_dqn['episode_reward']:
        sum_dqn += reward 
        total_reward_dqn.append(sum_dqn)

    total_reward_srs = []
    sum_srs = 0
    for reward in data_srs['episode_reward']:
        sum_srs += reward 
        total_reward_srs.append(sum_srs)

    fig, axs = plt.subplots(1, 2)

    axs[0].plot(x_srs, total_reward_srs)
    axs[0].set_title("SARSA RL method")

    axs[1].plot(x_dqn, total_reward_dqn)
    axs[1].set_title("DQN RL method")

    for ax in axs.flat:
        ax.set(xlabel='Episode number', ylabel='Cummulative reward')

    # Hide x labels and tick labels for top plots and y ticks for right plots.
    for ax in axs.flat:
        ax.label_outer()


    fig.tight_layout()
    plt.show()


def load_swarms_data():
    """Load data for different swarm configurations, from 2 to 5 robots."""

    json_2 = os.getenv("JSON_2_ROBOTS")
    json_3 = os.getenv("JSON_3_ROBOTS")
    json_4 = os.getenv("JSON_4_ROBOTS")
    json_5 = os.getenv("JSON_5_ROBOTS")

    with open(json_2) as json_file:
        data_2 = json.load(json_file)

    with open(json_3) as json_file:
        data_3 = json.load(json_file)

    with open(json_4) as json_file:
        data_4 = json.load(json_file)

    with open(json_5) as json_file:
        data_5 = json.load(json_file)

    x_2 = [(i+1) for i in range(len(data_2['episode_reward']))]
    x_3 = [(i+1) for i in range(len(data_3['episode_reward']))]
    x_4 = [(i+1) for i in range(len(data_4['episode_reward']))]
    x_5 = [(i+1) for i in range(len(data_5['episode_reward']))]

    fig, axs = plt.subplots(2, 2, sharey=True)

    axs[0, 0].plot(x_2, data_2["nb_steps"])
    axs[0, 0].set_title("2-robot formation")

    axs[0, 1].plot(x_3, data_3["nb_steps"])
    axs[0, 1].set_title("3-robot formation")

    axs[1, 0].plot(x_4, data_4["nb_steps"])
    axs[1, 0].set_title("4-robot formation")

    axs[1, 1].plot(x_5, data_5['nb_steps'])
    axs[1, 1].set_title("5-robot formation")

    for ax in axs.flat:
        ax.set(xlabel='Episode number', ylabel='Steps per episode')

    # Hide x labels and tick labels for top plots and y ticks for right plots.
    for ax in axs.flat:
        ax.label_outer()

    fig.tight_layout()
    plt.show()


def load():
    json_rnd = os.getenv("JSON_RND")
    json_dqn = os.getenv("JSON_DQN")
    json_srs = os.getenv("JSON_SRS")
    
    with open(json_rnd) as json_file:
        data_rnd = json.load(json_file)
    
    with open(json_dqn) as json_file:
        data_dqn = json.load(json_file)

    with open(json_srs) as json_file:
        data_srs = json.load(json_file)

    x_rnd = [(i+1) for i in range(len(data_rnd['episode_reward']))]
    reward_avg_rnd = [data_rnd['episode_reward'][i]/data_rnd['nb_episode_steps'][i] for i in range(len(data_rnd['episode_reward']))]
    x_dqn = [(i+1) for i in range(len(data_dqn['episode_reward']))]
    reward_avg_dqn = [data_rnd['episode_reward'][i]/data_dqn['nb_episode_steps'][i] for i in range(len(data_dqn['episode_reward']))]
    x_srs = [(i+1) for i in range(len(data_srs['episode_reward']))]
    reward_avg_srs = [data_srs['episode_reward'][i]/data_srs['nb_episode_steps'][i] for i in range(len(data_srs['episode_reward']))]

    fig, axs = plt.subplots(3, 2, sharey="col")

    axs[0, 0].plot(x_rnd, reward_avg_rnd)
    axs[0, 0].set_title("Random actions")

    axs[1, 0].plot(x_dqn, reward_avg_dqn)
    axs[1, 0].set_title("DQN RL method")
    
    axs[2, 0].plot(x_srs, reward_avg_srs)
    axs[2, 0].set_title("SARSA RL method")

    axs[0, 1].plot(x_rnd, data_rnd['nb_episode_steps'])
    axs[0, 1].set_title("Random actions")

    axs[1, 1].plot(x_dqn, data_dqn['nb_episode_steps'])
    axs[1, 1].set_title("DQN RL method")
    
    axs[2, 1].plot(x_srs, data_srs['nb_episode_steps'])
    axs[2, 1].set_title("SARSA RL method")

    labels = ['Average reward', 'Steps per episode', 
              'Average reward', 'Steps per episode', 
              'Average reward', 'Steps per episode']
    
    i = 0
    for ax in axs.flat:

        if i < 4:
            ax.set(ylabel=labels[i])
        else:
            ax.set(xlabel='Episode number', ylabel=labels[i])
        i += 1

    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    load_swarms_data()
    # load_200()