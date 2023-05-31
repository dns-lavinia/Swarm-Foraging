import os
import json

import matplotlib.pyplot as plt

def main():
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



if __name__ == "__main__":
    main()