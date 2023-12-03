from typing import List
from typing import Tuple
import itertools
import copy

from surveillance.environment import Environment
from surveillance.sensors.base import Sensor, SensorType
from surveillance.helpers import Pose
from surveillance.roombuilder.roombuilder import RoomMap


def _get_number_cycles(graph: dict) -> int:
    """
    Determine the number of cycles present in the given graph this needs to
    ignore the bidirectional edges
    """
    edges = set()
    for node in graph:
        for neighbor in graph[node]['neighbors']:
            # Make the edge representation, have the smaller node always
            # come first to avoid duplicates (i.e. (1, 2) and (2, 1))
            edge = (min(node, neighbor), max(node, neighbor))
            if edge not in edges:
                edges.add(edge)

    return len(edges) - len(graph) + 1


def _get_hallways(room_map: RoomMap) -> List[int]:
    hallways = []
    for node in room_map.reduced_graph:
        if room_map._is_hallway_node(node):
            hallways.append(node)
    return hallways


class Placement:
    """
    Handles the logic of determing the "optimal" placements of the given
    sensors in the given environment.
    """
    def __init__(self, environment: Environment):
        self.environment = environment

    def get_placement(self, sensors: List[Sensor]) -> List[Tuple[Sensor, Pose]]:
        """

        :return: A list that is made up of sensors and their cooresponding
                 placement
        """
        hallways = _get_hallways(self.environment.room_map)

        num_line_sensor = len([sensor for sensor in sensors if sensor.sensor_type == SensorType.LINE])

        # Generate all combinations of line sensors
        line_sensor_placements = list(itertools.combinations(hallways, num_line_sensor))

        # Go through all combinations and calculate the number of cycles
        # each combination would create
        placement_performances: List[int, List] = []
        for placement in line_sensor_placements:
            # Make a copy of the reduced_graph
            graph = copy.deepcopy(self.environment.room_map.reduced_graph)

            # Remove the nodes that are in the placement
            for node in placement:
                graph = self.environment.room_map._remove_node_from_graph(graph, node)

            # Remove nodes that no longer have any neighbors, this throws off
            # the cycle calculation
            nodes = list(graph.keys())
            for node in nodes:
                if len(graph[node]['neighbors']) == 0:
                    graph = self.environment.room_map._remove_node_from_graph(graph, node)

            # Now calculate the number of cycles on the graph with the
            # line sensors segmenting the hallways
            num_cycles = _get_number_cycles(graph)

            placement_performances.append((num_cycles, placement))

        # Sort the placements by the number of cycles they create
        placement_performances.sort(key=lambda x: x[0])
        placement_performances

        return []
