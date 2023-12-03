from typing import List
from typing import Tuple
import itertools
import copy
import statistics

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


def _get_sub_graph_sizes(graph: dict) -> List[int]:
    """
    Count the number of nodes in each subgraph of the larger graph
    """
    sub_graphs: List[set] = []

    for node in graph:
        sub_graph_index = None
        # Check if the node is already assigned a subgraph
        for (index, sub_graph) in enumerate(sub_graphs):
            if node in sub_graph:
                sub_graph_index = index
                break

        # If the node is not assigned a subgraph, make one for it
        if sub_graph_index is None:
            new_sub_graph = set()
            new_sub_graph.add(node)
            new_sub_graph.update(graph[node]['neighbors'])
            sub_graphs.append(new_sub_graph)
        # If the node is assigned a subgraph, add the neighbors to the
        # subgraph
        else:
            sub_graphs[sub_graph_index].update(graph[node]['neighbors'])

    return [len(sub_graph) for sub_graph in sub_graphs]


class Placement:
    """
    Handles the logic of determing the "optimal" placements of the given
    sensors in the given environment.
    """
    def __init__(self, environment: Environment):
        self.environment = environment

    def _get_line_sensor_placement(self, sensors: List[Sensor]) -> List[Tuple[Sensor, Pose]]:
        """
        Get the placement of the line sensors in the environment as well as
        how the graph is segmented by the line sensors
        """
        hallways = _get_hallways(self.environment.room_map)

        num_line_sensor = len([sensor for sensor in sensors if sensor.sensor_type == SensorType.LINE])

        # No line sensors, do not continue
        if num_line_sensor == 0:
            return [], self.environment.room_map.reduced_graph

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

        # Sort the placements by the number of cycles left in the graph
        placement_performances.sort(key=lambda x: x[0])

        # Keep top placements
        least_cycles = placement_performances[0][0]
        top_placements = [placement for placement in placement_performances if placement[0] == least_cycles]

        # Only one combination will remove the most cycles, so use this
        # combination
        if len(top_placements) == 0:
            # Get the nodes of the ideal placements
            nodes = top_placements[0][1]

            # Update the graph with the nodes removed
            graph = copy.deepcopy(self.environment.room_map.reduced_graph)
            for node in nodes:
                graph = self.environment.room_map._remove_node_from_graph(graph, node)

            # Return the placement and resulting graph
            return nodes, graph

        # Multiple combinations exist, now determine the size of all graphs
        placements = [placement[1] for placement in top_placements]
        placement_performances: List[int, List] = []
        for placement in placements:
            # Make a copy of the reduced_graph
            graph = copy.deepcopy(self.environment.room_map.reduced_graph)

            # Remove the nodes that are in the placement
            for node in placement:
                graph = self.environment.room_map._remove_node_from_graph(graph, node)

            graph_sizes = _get_sub_graph_sizes(graph)
            placement_performances.append((statistics.stdev(graph_sizes), placement))

        # Sort the placements by the number of cycles left in the graph
        placement_performances.sort(key=lambda x: x[0])
        print(placement_performances)

        # Get the nodes of the ideal placements
        nodes = placement_performances[0][1]

        # Update the graph with the nodes removed
        graph = copy.deepcopy(self.environment.room_map.reduced_graph)
        for node in nodes:
            graph = self.environment.room_map._remove_node_from_graph(graph, node)
        return nodes, graph

    def get_placement(self, sensors: List[Sensor]) -> List[Tuple[Sensor, Pose]]:
        """

        :return: A list that is made up of sensors and their cooresponding
                 placement
        """
        line_sensor_placements, graph = self._get_line_sensor_placement(sensors)

        return []
