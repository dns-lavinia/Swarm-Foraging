import math
import pygame

# Local imports
import constants 
    
                 
class LaserSensor:
    def __init__(self, range=400, n_readings=13, start_angle=-90, 
                 angle_space=15, position=(0,0), body_angle=0):
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

            position  (int, optional): The position where the LaserSensor is 
            placed on in the pymunk space.

            body_angle  (int, optional): The orientation of the body that is 
            to be placed on.
        """

        self.range = range
        self.n_readings = n_readings
        self.start_angle = start_angle
        self.angle_space = angle_space  # Leave this amount of space between readings

        # Body dependent parameters
        self.position = (position[0]+ 100, position[1])
        self.sensor_angle = body_angle

        # Save the pygame surface of the arena
        self.screen = pygame.display.get_surface()

    def __get_dist(self, obj_pos):
        """Returns the distance from the position of the laser itself to an
        object in the environment.
        """

        return math.sqrt((obj_pos[0] - self.position[0]) ** 2 + \
                         (obj_pos[1] - self.position) ** 2)
    
    def __get_fin_pos(self, angle):
        """Return the position at the extremity of the beam given the angle from
        the starting point.
        """

        # Convert the angle in degrees to radians
        angle_rad = math.radians(angle)

        # Get the x coordonate for the point in the 
        # extremity of the current beam
        x_fin = self.position[0] + self.range * math.cos(angle_rad)

        # Get the y coordinate for the point in the 
        # extremity of the current beam
        y_fin = self.position[1] + self.range * math.sin(angle_rad)

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
        if an object was found."""
        
        x_start, y_start = self.position[0], self.position[1]
        arena_w, arena_h = self.screen.get_size()

        for angle_idx in range(self.n_readings):
            angle = math.degrees(self.sensor_angle) + self.start_angle + \
                    angle_idx * self.angle_space
            
            # Get the position of the extremity of the beam
            x_fin, y_fin = self.__get_fin_pos(angle)

            # Along the line of the beam, check if there is any object 
            # TODO: find an analytical way to decide from what i should start
            # as an object shouldn't detect itself 
            for i in range(5, 100):
                u = i / 100

                # Get the position on the line
                x = int((1-u) * x_start + u * x_fin)
                y = int((1-u) * y_start + u * y_fin)

                # If the point is still within the screen coordonates
                if 0 < x < arena_w and 0 < y < arena_h:
                    # Get the color of the point 
                    color = self.screen.get_at((x, y))
                    
                    # If the color is different from the background of the 
                    # screen, then an objstacle was found
                    if (color[0], color[1], color[2]) != constants.COLOR["artichoke"]:
                        # print("detected object", time.time())

                        break 
            
        return False

    # TODO: draw this better
    def draw_sensor_angles(self):
        for angle_idx in range(self.n_readings):
            angle = math.degrees(self.sensor_angle) + self.start_angle + \
                    angle_idx * self.angle_space

            # Get the position of the extremity of the beam
            pos_fin = self.__get_fin_pos(angle)

            pygame.draw.line(self.screen, (255, 0, 0), self.position, pos_fin, 1)
