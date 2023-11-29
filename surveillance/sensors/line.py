from surveillance.sensors.base import Sensor
from matplotlib.axes._axes import Axes
from surveillance.environment import Environment
import numpy as np
from typing import Tuple


class LineSensor(Sensor):
    def __init__(self, pixel_to_cm: float, environment: Environment, config):
        super().__init__(pixel_to_cm, environment, config)

        self.max_length = config.get('max_length', np.inf)

    def _get_endpoints(self) -> Tuple[float, float]:
        """
        Get the end points of the line sensor based on the current
        location and orientation
        """
        if self.x is None or self.y is None or self.theta is None:
            raise Exception('Cannot display before sensor is places')

        distance = 0
        self.next_x = self.x
        self.next_y = self.y

        while distance < self.max_length:
            distance += 1

            # Calculate the next point
            next_x = self.x + distance * np.cos(self.theta)
            next_y = self.y + distance * np.sin(self.theta)

            # Check if the next point is in the environment
            if not self.environment.in_environment(next_x, next_y):
                break

            # Check if the next point is in an object
            if self.environment.in_object(next_x, next_y):
                break
        return next_x, next_y

    def display(self, ax: Axes) -> None:
        if self.x is None or self.y is None or self.theta is None:
            raise Exception('Cannot display before sensor is places')

        # Start at the given point
        start_point_x = self.x
        start_point_y = self.y

        # Get the end point
        end_point_x, end_point_y = self._get_endpoints()

        # Plot the line
        ax.plot([start_point_x, end_point_x], [start_point_y, end_point_y],
                'b-')

        # Plot a point at the start
        ax.plot(start_point_x, start_point_y, 'bo')

    def advisary_detected(self) -> bool:
        """
        Ray trace and determine if an advisary is detected
        """
        if self.x is None or self.y is None or self.theta is None:
            raise Exception('Cannot display before sensor is places')

        # Get the end point
        end_point_x, end_point_y = self._get_endpoints()
        length = np.sqrt((end_point_x - self.x)**2 + (end_point_y - self.y)**2)

        # Check in 1 cm increments from start point to end point
        for distance in np.arange(0, length, 1):
            # Calculate the next point
            next_x = self.x + distance * np.cos(self.theta)
            next_y = self.y + distance * np.sin(self.theta)

            # Check if the next point is in the environment
            if not self.environment.in_environment(next_x, next_y):
                return False

            # Check if the next point is in an object
            if self.environment.in_object(next_x, next_y):
                return False

            # Check if the next point is in the adversary
            if self.environment.in_adversary(next_x, next_y):
                return True

        return False
