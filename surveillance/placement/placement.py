from typing import List
import copy

from surveillance.environment import Environment
from surveillance.sensors.base import Sensor
from surveillance.placement.line import LineSensorPlacement
from surveillance.placement.camera import CameraSensorPlacement
from surveillance.placement.robot import RobotPlacement
from surveillance.placement.step import PlacementStep, PlacementResult


class Placement:
    """
    Handles the logic of determing the "optimal" placements of the given
    sensors in the given environment.
    """
    def __init__(self, environment: Environment):
        self.environment = environment

        self.steps: List[PlacementStep] = [
            LineSensorPlacement(self.environment),
            CameraSensorPlacement(self.environment),
            RobotPlacement(self.environment)
        ]

    def get_placement(self, sensors: List[Sensor]) -> PlacementResult:
        """

        :return: A list that is made up of sensors and their cooresponding
                 placement
        """
        placements = []
        sensors = sensors.copy()

        graph = copy.deepcopy(self.environment.room_map.reduced_graph)

        for step in self.steps:
            # Get the result of the step
            result = step.place(sensors, graph)

            # Remove the sensors that were placed from the list of sensors
            # that need to be placed
            for placement in result.placements:
                sensors.remove(placement.sensor)

            placements.extend(result.placements)

            # Update the graph
            graph = result.graph

        return PlacementResult(graph, placements)
