from typing import List
from typing import Tuple

from surveillance.environment import Environment
from surveillance.sensors.base import Sensor
from surveillance.helpers import Pose


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
        print(_get_number_cycles(self.environment.room.reduced_graph))
        return []
