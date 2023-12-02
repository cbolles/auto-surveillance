from typing import List

from matplotlib.axes._axes import Axes
import matplotlib.pyplot as plt
import numpy as np

from surveillance.base import SurveillanceObject
from surveillance.environment import Environment


class Adversary(SurveillanceObject):
    def __init__(self, pixel_to_cm: float, config):
        SurveillanceObject.__init__(self, pixel_to_cm)
        self.radius = config.get('radius', 10)
        self.environment = None

    def display(self, ax: Axes) -> None:
        """
        Display adversary as a point
        """
        x_pos = self.x * self.cm_to_pixel
        y_pos = self.y * self.cm_to_pixel
        circle = plt.Circle((x_pos, y_pos), self.radius * self.cm_to_pixel,
                            color='r')
        ax.add_artist(circle)

    def set_environment(self, environment: Environment) -> None:
        self.environment = environment

    def in_adversary(self, x: float, y: float) -> bool:
        """
        Check if a given point is within the adversary
        """
        distance = np.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
        return distance <= self.radius

    def update(self) -> None:
        """
        TODO: Implement motion logic into adversary
        """
        pass


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
