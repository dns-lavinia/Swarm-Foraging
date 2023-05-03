import sys 
import random 
import math

import pymunk
import pymunk.pygame_util
import pygame

from pymunk.vec2d import Vec2d

# Local imports
import constants

# Have the same results with every run of the simulation
random.seed(1)

def random_sign():
    return 1 if random.randint(0, 2) < 1 else -1


class LaserSensor:
    def __init__(self, range=400, n_angles=13, start_angle=-90, 
                 angle_space=15, position=(0,0), obj_angle=0):
        """Initialize the sensor

        Args:
            max_range (int, optional): The maximum range that the sensor can work 
            at. By default the sensor works from 0 to 400 cm.
            
            n_angles  (int, optional): The number of rays.By default the sensor
            gets 13 angular readings.

            start_angle  (int, optional): The starting angle in degrees (considering
            that the starting point is on the left side)
            
            angle_space  (int, optional): The space between the rays. By default
            the space between rays is 15 degrees.

            position  (int, optional): The position where the LaserSensor is 
            placed on in the pymunk space.
        """

        self.range = range
        self.n_angles = n_angles
        self.angle_space = angle_space  # Leave this amount of space between rays
        self.position = (position[0]+ 100, position[1])
        self.start_angle = start_angle
        self.sensor_angle = obj_angle

        # Save the pygame surface of the arena
        self.screen = pygame.display.get_surface()

    def __get_dist(self, obj_pos):
        """Returns the distance from the position of the laser itself to an
        object in the environment.
        """

        return math.sqrt((obj_pos[0] - self.position[0]) ** 2 + \
                         (obj_pos[1] - self.position) ** 2)
    
    
    def __get_fin_pos(self, angle):
        """Return the position at the extremity of the ray given the angle from
        the starting point.
        """

        # Convert the angle in degrees to radians
        angle_rad = math.radians(angle)

        # Get the x coordonate for the point in the 
        # extremity of the current ray
        x_fin = self.position[0] + self.range * math.cos(angle_rad)

        # Get the y coordinate for the point in the 
        # extremity of the current ray
        y_fin = self.position[1] + self.range * math.sin(angle_rad)

        return x_fin, y_fin


    def update_position(self, pos, angle):
        """Update the position of the laser by also taking into the consideration
        the orientation it has on the object it is placed on.

        Args:
            pos:  position of the object (robot)
            angle:  angle of the object (robot)
        """
        self.position = pos
        self.sensor_angle = angle
    
    def get_reading(self):
        # For every ray in the sensor, get a reading along its axis and check
        # if an object was found

        x_start, y_start = self.position[0], self.position[1]
        arena_w, arena_h = self.screen.get_size()

        for angle_idx in range(self.n_angles):
            angle = math.degrees(self.sensor_angle) + self.start_angle + angle_idx * self.angle_space
            
            # Get the position of the extremity of the ray
            x_fin, y_fin = self.__get_fin_pos(angle)

            # Along the ray, check if there is any object 
            for i in range(5, 100):
                u = i / 100

                # Get the position on the ray
                x = int((1-u) * x_start + u * x_fin)
                y = int((1-u) * y_start + u * y_fin)

                # If the point is still within the arena coordonates
                if 0 < x < arena_w and 0 < y < arena_h:
                    # Get the color of the point 
                    color = self.screen.get_at((x, y))

                    if (color[0], color[1], color[2]) != constants.COLOR["artichoke"]:
                        # print("detected object", time.time())

                        break 
            
        return False
    

    def draw_sensor_angles(self):
        for angle_idx in range(self.n_angles):
            angle = math.degrees(self.sensor_angle) + self.start_angle + angle_idx * self.angle_space

            # Get the position of the extremity of the ray
            pos_fin = self.__get_fin_pos(angle)

            pygame.draw.line(self.screen, (255, 0, 0), self.position, pos_fin, 1)


# NOTE: The emulated Lidar sensor has a detection range of 0 to 4m of 360 degrees
# and it was discretized using 13 angular readings
class SRobot: 
    MASS = 0.65  # kg
    RADIUS = 10  # cm

    def __init__(self, space, homebase_pos):
        # Spawn the robot in the vicinity of the home base
        x = homebase_pos[0] + random_sign() * random.randint(20, 40)
        y = homebase_pos[1] + random_sign() * random.randint(20, 40)

        # Create the body of the robot
        self.body = self.__add_robot_body(space, position=(x, y))

        # Attach a LaserSensor to it
        self.sensor = LaserSensor(position=(x, y), obj_angle=self.body.angle)
    
    # TODO: this function will be changed accordingly when RL will be added
    # source: https://github.com/viblo/pymunk/blob/master/pymunk/examples/tank.py 
    def update(self, space, dt, target_pos):
        """Update the position of the robot."""

        self.sensor.get_reading()
        
        target_delta = target_pos - self.body.position
        turn = self.body.rotation_vector.cpvunrotate(target_delta).angle 
        self.body.angle = self.body.angle - turn

        # Drive the robot towards the target object
        if (target_pos - self.body.position).get_length_sqrd() < 30 ** 2:
            # If the robot is close enough to the target object, stop
            self.body.velocity = 0, 0
        else:
            if target_delta.dot(self.body.rotation_vector) > 0.0:
                direction = 1.0
            else:
                direction = -1.0

            dv = Vec2d(30.0 * direction, 0.0)
            self.body.velocity = self.body.rotation_vector.cpvrotate(dv)

        space.step(dt)

        # Update the position of the sensor
        self.sensor.update_position(self.body.position, self.body.angle)

    def perception_sensor(self):
        return 0    

    def __add_robot_body(self, space, position):
        """Create and add to the space a box shape for the robot body.
        
        size[cm]; mass[kg]"""
    
        body = pymunk.Body()
        body.position = position

        shape = pymunk.Circle(body, self.RADIUS)
        
        # Add the attributes of the robot's body
        shape.mass = self.MASS
        shape.friction = 1
        shape.color = constants.COLOR["grey"]

        # Add the body to the space
        space.add(body, shape)

        return body


def main():   
    pygame.init()

    # Set the screen dimensions 
    screen = pygame.display.set_mode(constants.BOARD_SIZE)
    
    # Set the title of the simulation
    pygame.display.set_caption("Foraging in Swarm Robotics")
    clock = pygame.time.Clock()

    # Considering the screen variable above, the space would
    # occupy this whole screen and would have a dimension of 
    # 500cm x 500cm
    space = pymunk.Space()
    space.graivty = (0.0, 9.81)

    target = add_target(space)
    homebase = add_homebase(space)
    homebase_center = int(homebase.body.position.x) + 10, int(homebase.body.position.y)
    
    robots = []
    for _ in range(constants.ROBOTS_NUMBER):
        robots.append(SRobot(space, homebase.body.position))

    # Declare the optional attributes of the space
    draw_options = pymunk.pygame_util.DrawOptions(screen)

    # Simulation loop
    while True:
        # Finish the execution of the game when a key/button is pressed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                sys.exit(0)

        # Advance the simulation with one step
        space.step(1/constants.FPS) 
        
        # Make the background green
        screen.fill(constants.COLOR["artichoke"])

        # Draw area around the homebase
        pygame.draw.circle(surface=screen, 
                           color=constants.COLOR["carmine"], 
                           center=homebase_center, 
                           radius=25, 
                           width=1)

        space.debug_draw(draw_options)

        for i in range(constants.ROBOTS_NUMBER):
            robots[i].update(space, 1 / constants.FPS, target.body.position)
            robots[i].sensor.draw_sensor_angles()

        pygame.display.flip()
        clock.tick(constants.FPS)


def add_target(space):
    """create and add to the space the target object that is to be carried by
    the robots to the home base."""

    mass = 1  # Mass in kg
    length = 20  # Length in cm

    body = pymunk.Body()

    # Spawn the robot in the lower right area
    x = random.randint(400, 420)
    y = random.randint(80, 120)

    # Set the initial position of the robot
    body.position = x, y 

    # Add a square shape for the robot
    shape = pymunk.Poly.create_box(body, (length, length), 0.0)
    shape.color = constants.COLOR["hunter-green"]
    shape.mass = mass 
    shape.friction = 1

    # Add the target object to the sapce
    space.add(body, shape)

    return shape


def add_homebase(space):
    """Create and add to the space the homebase flag"""

    flag_sizes = [(25, 0), (0, 7), (0, -7)]
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    
    x = random.randint(50, 80)
    y = random.randint(400, 420)

    body.position = x, y 
    
    shape = pymunk.Poly(body, flag_sizes)
    shape.color = constants.COLOR["auburn"]
    
    space.add(body, shape)
    return shape


if __name__ == "__main__":
    sys.exit(main())