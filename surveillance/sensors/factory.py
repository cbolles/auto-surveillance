from surveillance.environment import Environment
from surveillance.sensors.base import Sensor, SensorType
from surveillance.sensors.line import LineSensor
from surveillance.sensors.camera import CameraSensor
from surveillance.sensors.robot import Robot


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
        sensor_type = SensorType(config['type'])
        if sensor_type == SensorType.LINE:
            return LineSensor(self.pixel_to_cm, self.environment, config)
        if sensor_type == SensorType.CAMERA:
            return CameraSensor(self.pixel_to_cm, self.environment, config)
        if sensor_type == SensorType.ROBOT:
            return Robot(self.pixel_to_cm, self.environment, config)
        else:
            raise Exception('Unsupported type: {}'.format(config['type']))
