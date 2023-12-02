from abc import ABC, abstractmethod
from matplotlib.axes._axes import Axes


class SurveillanceObject(ABC):
    """
    Generic surveillance object that defines basic methods for simulation
    and display
    """
    def __init__(self, pixel_to_cm: float):
        self.x = None
        self.y = None
        self.theta = None

        self.cm_to_pixel = 1 / pixel_to_cm

    @abstractmethod
    def display(self, ax: Axes) -> None:
        """
        Display the object on the given axes
        """
        pass

    @abstractmethod
    def update(self) -> None:
        """
        Update the state of the surveillance object. This is called once
        a timestep and intended to be used for things like motion and other
        changes
        """
        pass

    def place(self, x: float, y: float, theta: float) -> None:
        """
        Set the location and orientation of the given object

        :param x: The x location in CMs
        :param y: The y location in CMs
        :param theta: The angle in radians
        """
        self.x = x
        self.y = y
        self.theta = theta
