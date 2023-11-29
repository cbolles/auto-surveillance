from abc import ABC, abstractmethod
from matplotlib.axes._axes import Axes

from surveillance.environment import Environment


class Sensor(ABC):
    def __init__(self, pixel_to_cm: float, environment: Environment, config):
        """

        :param pixel_to_cm: How each pixel in the map maps to CMs
        """
        self.x = None
        self.y = None
        self.theta = None

        self.environment = environment

        self.cm_to_pixel = 1 / pixel_to_cm

    @abstractmethod
    def display(self, ax: Axes) -> None:
        """
        Visualize the sensor on the given axis
        """
        pass

    @abstractmethod
    def advisary_detected(self) -> bool:
        """
        Determine if an advisary is detected by the given sensor
        """
        return False

    def place(self, x: float, y: float, theta: float) -> None:
        """
        Set the location and orientation of the sensor

        :param x: The x location in CMs
        :param y: The y location in CMs
        :param theta: The angle in radians
        """
        self.x = x
        self.y = y
        self.theta = theta
