from abc import abstractmethod
from surveillance.environment import Environment
from surveillance.base import SurveillanceObject
from surveillance.adversary import AdversaryPool


class Sensor(SurveillanceObject):
    def __init__(self, pixel_to_cm: float, environment: Environment, config):
        super().__init__(pixel_to_cm)
        self.environment = environment

    @abstractmethod
    def adversary_detected(self, adversary_pool: AdversaryPool) -> bool:
        """
        Determine if an advisary is detected by the given sensor
        """
        return False
