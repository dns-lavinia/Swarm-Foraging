from keras.models import Sequential
from keras.layers import Dense

# Local imports 
from swarm import SwarmController

# action = the action the robot takes, meaning, the vrot, vtrans and scaling
# move the robot with the given action
# after the new action is decided by the nn, then I fit it and update state

# inputs of the nn: S = (obj_x, obj_y, goal_x, goal_y, f_r_rot, f_r_sca)

def create_nn():
    model = Sequential()
    model.add(Dense(64, activation="tanh", input_dim=6))
    model.add(Dense(64, activation="tanh"))
    model.add(Dense(3, activation="linear")) # linear activation

    # Compile the model
    model.compile(loss='mse', optimizer='adam')

    return model


run_episodes():
    discount_factor = 0.95
    eps = 0.5
    eps_decay_factor = 0.999
    n_episodes = 3 

    sim = Simulation()
    model = create_nn()

    for _ in range(n_episodes):
        state = sim.reset()  # reset the environment 
        eps *= eps_decay_factor 
        done = False 
        sim_steps = constants.MAX_SIM_STEPS

        # Run as long as the maximum simulation steps number is not reached and 
        # as long as the robots did not reach the goal with the target
        while not done:
            if np.random.random() < eps:
                # Get a random action
                action = np.random.randint(0, sim.ACTION_SPACE_N)
            else:
                action = np.argmax(model.predict(np.identity(sim.OBSERVATION_SPACE_N)[state:state+1]))
            
            new_state, reward, done = sim.step(action)

            target = reward \
                     + discount_factor * np.max(model.predict(np.identity(sim.OBSERVATION_SPACE_N)[state:state+1]))

            target_vector = model.predict(np.identity(sim.OBSERVATION_SPACE_N)[state:state+1])[0]
            target_vector[action] = target 

            # Train the model
            model.fit(
                np.identity(sim.OBSERVATION_SPACE_N)[state:state+1],
                target_vector.reshape(-1, sim.ACTION_SPACE_N),
                epochs=1, verbose=0
            )

            state = new_state

            # Update the remaining simulation steps
            sim_steps -= 1

            # Update done
            done = done | (sim_steps > 0) 


if __name__ == "__main__":
    run_episodes()