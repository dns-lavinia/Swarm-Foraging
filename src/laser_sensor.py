import math
import pygame
import numpy as np

# Local imports
import constants 


# This class was based on the sensor.py module that can be found at:   
# https://github.com/charleslf2/2D-simulation-of-Simulataneous-Localisation-And-Maping-SLAM-               
class LaserSensor:
    def __init__(self, range=400, n_readings=13, start_angle=-90, 
                 angle_space=15, position=(0,0), body_angle=0, body_radius=10):
        """Initialize the sensor.

        Args:
            max_range (int, optional): The maximum range that the sensor can work 
            at. By default the sensor works from 0 to 400 cm.
            
            n_readings  (int, optional): The number of angular readings performed
            by the sensor.

            start_angle  (int, optional): The starting angle in degrees (considering
            that the starting point is on the left side)
            
            angle_space  (int, optional): The space in degrees between the 
            angular readings. Defaults to 15 (degrees).

            position  ((int, int), optional): The position where the LaserSensor is 
            placed on in the pymunk space.

            body_angle  (int, optional): The orientation of the body that is 
            to be placed on.

            body_radius (int, optional): The width of the body the sensor is placed
            on. It is assumed that the body has a circular shape.
        """

        self.range = range
        self.n_readings = n_readings
        self.start_angle = start_angle
        self.angle_space = angle_space  # Leave this amount of space between readings

        # Body dependent parameters
        self.position = (position[0]+100, position[1])
        self.sensor_angle = body_angle
        self.body_radius = body_radius

        # Save the pygame surface of the arena
        self.screen = pygame.display.get_surface()

    def __get_dist(self, obj_pos):
        """Returns the distance from the position of the laser itself to an
        object in the environment.
        """

        return math.sqrt((obj_pos[0] - self.position[0]) ** 2 + \
                         (obj_pos[1] - self.position[1]) ** 2)
    
    def __get_fin_pos(self, angle, length):
        """Return the position at the extremity of the ray given the angle from
        the starting point.

        Args:
            angle: The angle at which the line is 
            length: The length of the line
        """

        # Convert the angle in degrees to radians
        angle_rad = math.radians(angle)

        # Get the x coordonate for the point in the 
        # extremity of the current ray
        x_fin = self.position[0] + length * math.cos(angle_rad)

        # Get the y coordinate for the point in the 
        # extremity of the current ray
        y_fin = self.position[1] + length * math.sin(angle_rad)

        return x_fin, y_fin

    def update_position(self, pos, angle):
        """Update the position of the laser by also taking into the consideration
        the orientation of the object it is placed on.

        Args:
            pos:  position of the object (robot)
            angle:  angle of the object (robot)
        """
        self.position = pos
        self.sensor_angle = angle
    
    def get_reading(self):
        """Perform all of the angular readings along the sensor's axis and check 
        if an object was found.
        
        Returns a list containing all angular readings.
        
        Args:
            obj_color (str): The color of the object to detect."""
        
        arena_w, arena_h = self.screen.get_size()
        readings = []

        for angle_idx in range(self.n_readings):
            angle = math.degrees(self.sensor_angle) + self.start_angle + \
                    angle_idx * self.angle_space
            
            # Get the first point on the line that is not within the body
            pos_start = self.__get_fin_pos(angle, self.body_radius)
            
            # Get the position of the extremity of the ray
            x_fin, y_fin = self.__get_fin_pos(angle, self.range)

            # Flag used to check if an object was found for every reading
            found_object = False

            # Along the line of the ray, check if there is any object 
            for i in range(0, 150):
                u = i / 150

                # Get the position on the line
                x_line = int((1-u) * pos_start[0] + u * x_fin)
                y_line = int((1-u) * pos_start[1] + u * y_fin)

                # If the point is still within the screen coordonates
                if 0 < x_line < arena_w and 0 < y_line < arena_h:
                    # Get the color of the point 
                    color = self.screen.get_at((x_line, y_line))
                    
                    # If the color represents the color of an obstacle
                    if (color[0], color[1], color[2]) != constants.COLOR["artichoke"] or \
                        (color[0], color[1], color[2]) != constants.COLOR["auburn"]:
                        found_object = True

                        distance = self.__get_dist((x_line, y_line))
                        obstacle_data = self.__add_noise(distance, angle)

                        # Since an obstacle was found, add it to the list
                        # Record the position the obstacle was found at 
                        # and also the current position of the laser
                        readings.insert(angle_idx, obstacle_data[0])
                        
                        break 
            
            if not found_object:
                distance = self.__get_dist((x_fin, y_fin))
                data = self.__add_noise(distance, angle)

                readings.insert(angle_idx, data[0])
        
        # Return the coordinates of the obstacles or None if there isn't any
        return readings if len(readings) > 0 else None

    def draw_sensor_angles(self):
        for angle_idx in range(self.n_readings):
            angle = math.degrees(self.sensor_angle) + self.start_angle + \
                    angle_idx * self.angle_space
            
            # Get the first point on the line that is not within the body
            pos_start = self.__get_fin_pos(angle, self.body_radius)

            # Get the position of the extremity of the ray
            pos_fin = self.__get_fin_pos(angle, self.range)

            # Draw a red line representing the ray
            pygame.draw.line(self.screen, (255, 0, 0), pos_start, pos_fin, 2)
    
    def __add_noise(self, distance, angle):
        """Return the distance and the angle of the detected object with noise
        added to the measurement. This noise is simply a random value in the
        vicinity of the actual measurement."""
        
        sigma = np.array([0.5, 0.01])

        mean = np.array([distance, angle])
        cov = np.diag(sigma ** 2)

        # Get the new measurements with the added noise
        new_dist, new_angle = np.random.multivariate_normal(mean, cov)

        # Clip to 0 if the values are negative
        new_dist = max(new_dist, 0)
        new_angle = max(new_angle, 0)

        return new_dist, new_angle
