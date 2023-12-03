from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from surveillance.environment import Environment
from surveillance.sensors.base import Sensor
from surveillance.helpers import Pose


@dataclass
class Placement:
    sensor: Sensor
    pose: Pose


@dataclass
class PlacementResult:
    graph: dict
    placements: Placement


class PlacementStep(ABC):
    def __init__(self, environment: Environment):
        self.environment = environment

    @abstractmethod
    def place(self, sensors: List[Sensor], graph: dict) -> PlacementResult:
        pass
