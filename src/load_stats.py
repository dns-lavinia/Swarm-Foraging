import os
import json

import matplotlib.pyplot as plt

def load_old():
    path_to_json_files="data/"

    json_file_names = [filename for filename in os.listdir(path_to_json_files) if filename.endswith('.json')]

    for json_file_name in json_file_names:
        with open(os.path.join(path_to_json_files, json_file_name)) as json_file:
            # Plot the rewards per step
            data = json.load(json_file)

            rewards = [step for step in data['rewards_per_step']]
            x_rewards = [i for i in range(len(rewards))]

            plt.figure(1)
            plt.plot(x_rewards, rewards, label=json_file_name)
            plt.xlabel('Time step number')
            plt.ylabel('Total reward for timestep')
            leg = plt.legend(loc='upper center')

            y_timesteps = [ts for ts in data['timesteps_per_ep']] 
            x_timesteps = [i for i in range(len(y_timesteps))]

            # Plot the timesteps per episode
            plt.figure(2)
            plt.plot(x_timesteps, y_timesteps, label=json_file_name)
            plt.xlabel('The episode number')
            plt.ylabel('The number of timesteps')
            leg = plt.legend(loc='upper center')

            y_ep = [ep for ep in data['reward_per_ep']]
            y_ep_avg = [y_ep[i]/y_timesteps[i] for i in range(len(y_ep))]
            x_ep = [i for i in range(len(y_ep))]

            # Plot the average reward per epsiode
            plt.figure(3)
            plt.plot(x_ep, y_ep_avg, label=json_file_name)
            plt.xlabel('The episode number')
            plt.ylabel('The average reward')
            leg = plt.legend(loc='upper center')
    
    plt.show()


def load_one():
    json_file_name = "data/sarsa_data2023-06-21 14:18:26.602894.json"

    with open(json_file_name) as json_file:
        data = json.load(json_file)
        x = [(i+1) for i in range(len(data['episode_reward']))]

        reward_avg = [data['episode_reward'][i]/data['nb_episode_steps'][i] for i in range(len(data['episode_reward']))]

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

def load():
    json_rnd = "data/rnd_data2023-06-20 16:12:25.355010.json"
    json_dqn = "data/dqn_data2023-06-20 15:25:32.883070.json"
    json_srs = "data/sarsa_data2023-06-20 14:52:40.162071.json"
    
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
    load_one()