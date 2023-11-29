from surveillance.sensors.base import Sensor
from matplotlib.axes._axes import Axes
from surveillance.environment import Environment
import numpy as np


class LineSensor(Sensor):
    def __init__(self, pixel_to_cm: float, environment: Environment, config):
        super().__init__(pixel_to_cm, environment, config)

        self.max_length = config.get('max_length', np.inf)

    def display(self, ax: Axes) -> None:
        if self.x is None or self.y is None or self.theta is None:
            raise Exception('Cannot display before sensor is places')

        # Start at the given point
        start_point_x = self.x
        start_point_y = self.y

        # Ray trace until either the max length is reached or the ray hits an
        # object
        distance = 0
        while distance < self.max_length:
            distance += 1

            # Calculate the next point
            next_x = start_point_x + distance * np.cos(self.theta)
            next_y = start_point_y + distance * np.sin(self.theta)

            # Check if the next point is in the environment
            if not self.environment.in_environment(next_x, next_y):
                break

            # Check if the next point is in an object
            if self.environment.in_object(next_x, next_y):
                break

        # Calculate the endpoints based on the distance
        end_point_x = start_point_x + distance * np.cos(self.theta)
        end_point_y = start_point_y + distance * np.sin(self.theta)

        # Plot the line
        ax.plot([start_point_x, end_point_x], [start_point_y, end_point_y],
                'b-')

    def advisary_detected(self) -> bool:
        return False
