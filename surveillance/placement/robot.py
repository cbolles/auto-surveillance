import random
from typing import List

from surveillance.placement.step import PlacementStep, PlacementResult, Placement
from surveillance.environment import Environment
from surveillance.sensors.base import SensorType, Sensor
from surveillance.helpers import Pose, _get_rooms, node_to_px


class RobotPlacement(PlacementStep):
    def __init__(self, environment: Environment):
        super().__init__(environment)

    def place(self, sensors: List[Sensor], original_graph: dict) -> PlacementResult:
        """
        This is a simplified version of the placement that just places the
        robots in random room nodes. Ideally the placement is based on graphs
        that need to be explored
        """
        robot_sensors = [sensor for sensor in sensors if sensor.sensor_type == SensorType.ROBOT]

        # Get all the nodes that are in rooms
        room_nodes = _get_rooms(self.environment.room_map)

        # Place the robots in random rooms
        allocations = []
        for robot in robot_sensors:
            node = random.choice(room_nodes)
            allocations.append((robot, node))

        # Translate from box to pixels
        placements: List[Placement] = []
        for alloc in allocations:
            node_pos = self.environment.room_map.reduced_graph[alloc[1]]['pos']
            x, y = node_to_px(node_pos, self.environment.room_map.BOX_SIZE)
            placements.append(Placement(sensor=alloc[0], pose=Pose(x=x, y=y, theta=0)))

        return PlacementResult(graph=original_graph, placements=placements)
