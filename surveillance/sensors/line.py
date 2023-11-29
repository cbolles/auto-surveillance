from surveillance.sensors.base import Sensor
from matplotlib.axes._axes import Axes
from surveillance.environment import Environment


class LineSensor(Sensor):
    def display(self, ax: Axes) -> None:
        pass

    def advisary_detected(self, env: Environment) -> bool:
        return False
