from typing import List
import itertools
import copy
import statistics

from surveillance.environment import Environment
from surveillance.sensors.base import Sensor, SensorType
from surveillance.placement.step import PlacementStep, PlacementResult, Placement
from surveillance.helpers import _get_hallways, _get_number_cycles, _get_sub_graph_sizes


class LineSensorPlacement(PlacementStep):
    def __init__(self, environment: Environment):
        super().__init__(environment)

    def place(self, sensors: List[Sensor], original_graph: dict) -> PlacementResult:
        """
        Get the placement of the line sensors in the environment as well as
        how the graph is segmented by the line sensors
        """
        hallways = _get_hallways(self.environment.room_map)

        line_sensors = [sensor for sensor in sensors if sensor.sensor_type == SensorType.LINE]
        num_line_sensor = len(line_sensors)

        # No line sensors, do not continue
        if num_line_sensor == 0:
            return [], original_graph

        # Generate all combinations of line sensors
        line_sensor_placements = list(itertools.combinations(hallways, num_line_sensor))

        # Go through all combinations and calculate the number of cycles
        # each combination would create
        placement_performances: List[int, List] = []
        for placement in line_sensor_placements:
            # Make a copy of the reduced_graph
            graph = copy.deepcopy(original_graph)

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
            graph = copy.deepcopy(original_graph)

            # Remove the nodes that are in the placement
            for node in placement:
                graph = self.environment.room_map._remove_node_from_graph(graph, node)

            graph_sizes = _get_sub_graph_sizes(graph)
            placement_performances.append((statistics.stdev(graph_sizes), placement))

        # Sort the placements by the number of cycles left in the graph
        placement_performances.sort(key=lambda x: x[0])

        # Get the nodes of the ideal placements
        nodes = placement_performances[0][1]

        # Update the graph with the nodes removed
        graph = copy.deepcopy(original_graph)
        for node in nodes:
            graph = self.environment.room_map._remove_node_from_graph(graph, node)

        placements = []
        for (index, node) in enumerate(nodes):
            # TODO: Replace with translation logic for node location to pose
            placements.append(Placement(line_sensors[index], self.environment.room_map.reduced_graph[node]['pos']))

        return PlacementResult(graph=graph, placements=placements)
