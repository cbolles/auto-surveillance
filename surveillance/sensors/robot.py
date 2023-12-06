from typing import Tuple
import math

import matplotlib.pyplot as plt
from matplotlib.axes._axes import Axes
import numpy as np

from surveillance.sensors.base import Sensor, SensorType
from surveillance.environment import Environment


class Robot(Sensor):
    """
    Robot is represented as a circle with a LIDAR sensor at its front with
    a configurable FOV and range
    """
    def __init__(self, pixel_to_cm: float, environment: Environment, config):
        super().__init__(pixel_to_cm, environment, config, SensorType.ROBOT)
        self.radius = config.get('radius', 10)
        self.speed = config.get('speed', 1)
        self.fov = config.get('fov', np.pi / 2)
        self.range = config.get('range', 100)
        self.angle_resolution = math.radians(config.get('angle_resolution', 1))
        self.environment = environment

    def _get_endpoint(self, theta: float) -> Tuple[float, float]:
        """
        Get the end points of the line originating at the camera at angle theta
        """
        if self.x is None or self.y is None or self.theta is None:
            raise Exception('Cannot display before sensor is placed')

        distance = 0
        self.next_x = self.x
        self.next_y = self.y

        while distance < self.range:
            distance += 1

            # Calculate the next point
            next_x = self.x + distance * np.cos(theta)
            next_y = self.y + distance * np.sin(theta)

            # Check if the next point is in the environment
            if not self.environment.in_environment(next_x, next_y):
                break

            # Check if the next point is in an object
            if self.environment.in_object(next_x, next_y):
                break

        return next_x, next_y

    def display(self, ax: Axes, color='b') -> None:
        """
        Display robot as a point
        """
        # Display the robot itself
        x_pos = self.x * self.cm_to_pixel
        y_pos = self.y * self.cm_to_pixel
        circle = plt.Circle((x_pos, y_pos), self.radius * self.cm_to_pixel,
                            color='b')
        ax.add_artist(circle)

        # Display the LIDAR, remove collisions with the environment
        for theta in np.arange(self.theta - self.fov / 2,
                               self.theta + self.fov / 2,
                               self.angle_resolution):
            # Get the end point
            end_point_x, end_point_y = self._get_endpoint(theta)

            # Plot the line
            ax.plot([x_pos, end_point_x * self.cm_to_pixel],
                    [y_pos, end_point_y * self.cm_to_pixel], 'b-')

    def update(self) -> None:
        """
        Movement with the robot moving forward or turning 90 degrees
        if it cannot move forward
        """
        # Check if the path forward is clear accounting for the radius
        x_i = self.x + self.speed * np.cos(self.theta)
        y_i = self.y + self.speed * np.sin(self.theta)

        # Get the point on the edge of the circle for bound checking
        x_i_r = x_i + self.radius * np.cos(self.theta)
        y_i_r = y_i + self.radius * np.sin(self.theta)

        if self.environment.in_environment(x_i_r, y_i_r) and \
                not self.environment.in_object(x_i_r, y_i_r):
            self.x = x_i
            self.y = y_i
        else:
            # Turn 90 degrees
            self.theta += np.pi / 2

    def adversary_detected(self, adversary_pool) -> bool:
        """
        Ray trace and determine if an adversary is detected
        """
        if self.x is None or self.y is None or self.theta is None:
            raise Exception('Cannot display before sensor is placed')

        for theta in np.arange(self.theta - self.fov / 2,
                               self.theta + self.fov / 2,
                               self.angle_resolution):
            # Get the end point
            end_point_x, end_point_y = self._get_endpoint(theta)
            length = np.sqrt((end_point_x - self.x)**2 + (end_point_y - self.y)**2)

            # Check in 1 cm increments from start point to end point
            for distance in np.arange(0, length, 1):
                # Calculate the next point
                next_x = self.x + distance * np.cos(theta)
                next_y = self.y + distance * np.sin(theta)

                # Check if the next point is in the adversary
                if adversary_pool.in_adversary(next_x, next_y):
                    return True

        return False
