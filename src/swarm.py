import math

import numpy as np

from keras.models import Sequential
from keras.layers import Dense 

# Local imports
from srobot import SRobot

# action = the action the robot takes, meaning, the vrot, vtrans and scaling
# move the robot with the given action
# after the new action is decided by the nn, then I fit it and update state

# inputs of the nn: S = (obj_x, obj_y, goal_x, goal_y, f_r_rot, f_r_sca)

class SwarmController:
    # The space that has to be left empty in the swarm formation cirlce
    U_SHAPE_ALPHA = (math.pi / 5) * 2
    SWARM_SIZE = 3

    def __init__(self, start_pos, start_angle, sim_space, *, swarm_size=SWARM_SIZE):
        self.space = sim_space

        self.swarm_size = swarm_size
        self.position = start_pos
        self.angle = start_angle  # in radians
        self.f_sca = 20  # Denotes the radius of the swarm formation

        # Compute the beta angle (in radians)
        self.b_angle = (2 * math.pi - self.U_SHAPE_ALPHA) / swarm_size

        # Add the robots in the swarm and place them in a U shape
        self.robots = self.__add_robots()

    def __add_robots(self):
        # Around the starting position, arrange the robots in a U shape
        robots = []
        for i in range(self.swarm_size):
            # Get the position of the robot in the formation
            pos = self.__get_robot_pos(angle=(i * self.b_angle))

            robots.append(SRobot(self.space, start_pos=pos))
        
        return robots
    
    def __get_robot_pos(self, angle):
        """Return the position of a robot for a given beta angle."""
        pos_x = self.position[0]  \
                + self.f_sca * math.cos(self.angle - self.U_SHAPE_ALPHA/2 - angle)
        
        pos_y = self.position[1] \
                + self.f_sca * math.sin(self.angle - self.U_SHAPE_ALPHA/2 - angle)

        return pos_x, pos_y 
        
    
def agent_controller():
    return


def create_nn():
    model = Sequential()
    model.add(Dense(64, activation="tanh", input_dim=6))
    model.add(Dense(64, activation="tanh"))
    model.add(Dense(3, activation="linear")) # linear activation

    # Compile the model
    model.compile(loss='mse', optimizer='adam', metrics=['mae'])

    return model


# def run_episodes():
    # discount_factor = 0.95
    # eps = 0.5
    # eps_decay_factor = 0.999
    # n_episodes = 3 

    # sim = Simulation()
    # model = create_nn()

    # for _ in range(n_episodes):
    #     state = sim.reset()  # reset the environment 
    #     eps *= eps_decay_factor 
    #     done = False 
    #     sim_steps = constants.MAX_SIM_STEPS

    #     # Run as long as the maximum simulation steps number is not reached and 
    #     # as long as the robots did not reach the goal with the target
    #     while not done:
    #         if np.random.random() < eps:
    #             # Get a random action
    #             action = np.random.randint(0, sim.ACTION_SPACE_N)
    #         else:
    #             action = np.argmax(model.predict(np.identity(sim.OBSERVATION_SPACE_N)[state:state+1]))
            
    #         new_state, reward, done, _ = sim.step(action)

    #         target = reward \
    #                  + discount_factor * np.max(model.predict(np.identity(sim.OBSERVATION_SPACE_N)[state:state+1]))

    #         target_vector = model.predict(np.identity(sim.OBSERVATION_SPACE_N)[state:state+1])[0]
    #         target_vector[action] = target 

    #         # Train the model
    #         model.fit(
    #             np.identity(sim.OBSERVATION_SPACE_N)[state:state+1],
    #             target_vector.reshape(-1, sim.ACTION_SPACE_N),
    #             epochs=1, verbose=0
    #         )

    #         state = new_state

    #         # Update the remaining simulation steps
    #         sim_steps -= 1

    #         # Update done
    #         done = done | (sim_steps > 0) 
