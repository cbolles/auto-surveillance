from typing import List

from matplotlib.axes._axes import Axes
import matplotlib.pyplot as plt
import numpy as np

from surveillance.base import SurveillanceObject
from surveillance.environment import Environment


class Adversary(SurveillanceObject):
    def __init__(self, pixel_to_cm: float, config, environment: Environment):
        SurveillanceObject.__init__(self, pixel_to_cm)
        self.radius = config.get('radius', 10)
        self.speed = config.get('speed', 1)
        self.environment = environment

    def display(self, ax: Axes) -> None:
        """
        Display adversary as a point
        """
        x_pos = self.x * self.cm_to_pixel
        y_pos = self.y * self.cm_to_pixel
        circle = plt.Circle((x_pos, y_pos), self.radius * self.cm_to_pixel,
                            color='r')
        ax.add_artist(circle)

    def in_adversary(self, x: float, y: float) -> bool:
        """
        Check if a given point is within the adversary
        """
        distance = np.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
        return distance <= self.radius

    def update(self) -> None:
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


class AdversaryPool:
    """
    Collection of the adversaries
    """
    def __init__(self, adversaries: List[Adversary]):
        self.adversaries = adversaries

    def in_adversary(self, x: float, y: float) -> bool:
        for adversary in self.adversaries:
            if adversary.in_adversary(x, y):
                return True
        return False
