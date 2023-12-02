from matplotlib.axes._axes import Axes
import matplotlib.pyplot as plt
import numpy as np
from surveillance.base import SurveillanceObject


class Adversary(SurveillanceObject):
    def __init__(self, pixel_to_cm: float, config):
        SurveillanceObject.__init__(self, pixel_to_cm)
        self.radius = config.get('radius', 10)

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
        """
        TODO: Implement motion logic into adversary
        """
        pass
