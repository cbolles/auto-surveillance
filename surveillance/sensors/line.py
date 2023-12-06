from surveillance.sensors.base import Sensor, SensorType
from matplotlib.axes._axes import Axes
from surveillance.environment import Environment
from surveillance.adversary import AdversaryPool
import numpy as np
from typing import Tuple


class LineSensor(Sensor):
    def __init__(self, pixel_to_cm: float, environment: Environment, config):
        super().__init__(pixel_to_cm, environment, config, SensorType.LINE)

        self.range = config.get('range', np.inf)

    def _get_endpoint(self) -> Tuple[float, float]:
        """
        Get the end point of the line sensor based on the current
        location and orientation
        """
        if self.x is None or self.y is None or self.theta is None:
            raise Exception('Cannot display before sensor is placed')

        distance = 0
        self.next_x = self.x
        self.next_y = self.y

        while distance < self.range:
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

    def display(self, ax: Axes, color='b') -> None:
        if self.x is None or self.y is None or self.theta is None:
            raise Exception('Cannot display before sensor is placed')

        # Start at the given point
        start_point_x = self.x
        start_point_y = self.y

        # Get the end point
        end_point_x, end_point_y = self._get_endpoint()

        # Plot the line
        ax.plot([start_point_x, end_point_x], [start_point_y, end_point_y],
                'b-')

        # Plot a point at the start
        ax.plot(start_point_x, start_point_y, 'bo')

    def adversary_detected(self, adversary_pool: AdversaryPool) -> bool:
        """
        Ray trace and determine if an adversary is detected
        """
        if self.x is None or self.y is None or self.theta is None:
            raise Exception('Cannot display before sensor is placed')

        # Get the end point
        end_point_x, end_point_y = self._get_endpoint()
        length = np.sqrt((end_point_x - self.x)**2 + (end_point_y - self.y)**2)

        # Check in 1 cm increments from start point to end point
        for distance in np.arange(0, length, 1):
            # Calculate the next point
            next_x = self.x + distance * np.cos(self.theta)
            next_y = self.y + distance * np.sin(self.theta)

            # Check if the next point is in the adversary
            if adversary_pool.in_adversary(next_x, next_y):
                return True

        return False

    def update(self) -> None:
        """
        Line sensor doesn't change between time steps
        """
        pass
