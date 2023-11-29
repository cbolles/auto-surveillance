from surveillance.environment import Environment
from surveillance.sensors.base import Sensor
from surveillance.sensors.line import LineSensor


class SensorFactory:
    """
    Factory to create instance of sensors based on the type provided
    in the config
    """
    def __init__(self, pixel_to_cm: float, environment: Environment):
        self.pixel_to_cm = pixel_to_cm
        self.environment = environment

    def construct(self, config) -> Sensor:
        """
        Based on the configuration, construct a new sensor
        """
        if config['type'] == 'Line':
            return LineSensor(self.pixel_to_cm, self.environment, config)
        else:
            raise Exception('Unsupported type: {}'.format(config['type']))
