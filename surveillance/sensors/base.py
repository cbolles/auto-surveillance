from abc import abstractmethod
from enum import Enum

from surveillance.environment import Environment
from surveillance.base import SurveillanceObject
from surveillance.adversary import AdversaryPool


class SensorType(Enum):
    LINE = 'Line'
    CAMERA = 'Camera'
    ROBOT = 'Robot'


class Sensor(SurveillanceObject):
    def __init__(self, pixel_to_cm: float, environment: Environment, config, sensor_type: SensorType):
        super().__init__(pixel_to_cm)
        self.environment = environment
        self.name = config.get('name', 'Unknown Sensor')
        self.sensor_type = sensor_type

    @abstractmethod
    def adversary_detected(self, adversary_pool: AdversaryPool) -> bool:
        """
        Determine if an advisary is detected by the given sensor
        """
        return False
