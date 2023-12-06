from typing import List, Tuple
import itertools
import copy
import statistics
import math

import numpy as np

from surveillance.environment import Environment
from surveillance.sensors.base import Sensor, SensorType
from surveillance.placement.step import PlacementStep, PlacementResult, Placement
from surveillance.helpers import _get_hallways, _get_number_cycles, _get_sub_graph_sizes, Pose


class LineSensorPlacement(PlacementStep):
    def __init__(self, environment: Environment):
        super().__init__(environment)

    def _get_least_cycles(self, original_graph: dict, line_sensors: List[Sensor], hallways: List[int]) -> List[Tuple]:
        """
        This will iterate through all possible combinations hallways where
        the line sensors could be placed and determine the number of cycles
        that would exist in the graph if the nodes in the placement were
        removed. The placement with the least number of cycles will be
        returned (likely a list of options)
        """
        # Generate all possible combinations of hallways that the line sensors
        # could be placed on
        num_line_sensor = len(line_sensors)
        line_sensor_placements = list(itertools.combinations(hallways, num_line_sensor))
        print('Number of combinations: {}'.format(len(line_sensor_placements)))

        # Go through all combinations and calculate the number of cycles
        # each combination would create
        placement_performances: List[Tuple[int, List]] = []
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

        # Return only the nodes, the cooresponding number of cycles is extra
        # knowledge that is not needed
        return [placement[1] for placement in top_placements]

    def _get_lowest_stddev(self, original_graph: dict, line_sensors: List[Sensor],
                           least_cycles: List[Tuple]) -> Tuple:
        """
        This will iterate through the split options (least_cycles) and
        determine the size of all sub graphs created if the nodes in the
        placement are removed. The placement with the lowest standard
        deviation of subgraph sizes will be returned.
        """
        placement_performances: List[Tuple[int, List]] = []
        for placement in least_cycles:
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
        return placement_performances[0][1]

    def place(self, sensors: List[Sensor], original_graph: dict) -> PlacementResult:
        """
        Place line sensors in the environment. Line sensors are placed in
        hallways with the following goals.

        1. Minimize the number of cycles in the graph
           This is the primary goal and how the options are sorted by first
           if there is a tie for least number of cycles, then the next
           step is used to break the tie.
        2. Minimize the standard deviation of the subgraph sizes
           This goal is to break the graph into subgraphs of similar sizes.
        """
        hallways = _get_hallways(self.environment.room_map)

        line_sensors = [sensor for sensor in sensors if sensor.sensor_type == SensorType.LINE]
        num_line_sensor = len(line_sensors)

        print('Number of hallways: {}, Number of line sensors: {}'.format(len(hallways), num_line_sensor))

        # No line sensors, do not continue
        if num_line_sensor == 0:
            return PlacementResult(placements=[], graph=original_graph)

        least_cycles = self._get_least_cycles(original_graph, line_sensors, hallways)

        # Only one combination will remove the most cycles, so use this
        # combination
        if len(least_cycles) == 0:
            # Get the nodes of the ideal placements
            nodes = least_cycles[0]

            # Update the graph with the nodes removed
            graph = copy.deepcopy(self.environment.room_map.reduced_graph)
            for node in nodes:
                graph = self.environment.room_map._remove_node_from_graph(graph, node)

            # Return the placement and resulting graph
            return PlacementResult(placements=nodes, graph=graph)

        lowest_std = self._get_lowest_stddev(original_graph, line_sensors, least_cycles)

        # Update the graph with the nodes removed
        graph = copy.deepcopy(original_graph)
        for node in lowest_std:
            graph = self.environment.room_map._remove_node_from_graph(graph, node)

        placements = []
        for (index, node) in enumerate(lowest_std):
            x_map = self.environment.room_map.reduced_graph[node]['pos'][0] * self.environment.room_map.BOX_SIZE
            y_map = self.environment.room_map.reduced_graph[node]['pos'][1] * self.environment.room_map.BOX_SIZE

            # First try ray tracing in the x direction
            theta = np.pi
            distance = 0
            found_wall = False
            while distance < self.environment.room_map.BOX_SIZE:
                distance += 1

                x = x_map + distance * math.cos(theta)
                y = y_map + distance * math.sin(theta)

                if self.environment.in_object(x, y):
                    found_wall = True
                    x = x_map + (distance - 1) * math.cos(theta)
                    y = y_map + (distance - 1) * math.sin(theta)
                    theta = 0
                    break

            if not found_wall:
                # Now try ray tracing in the y direction
                theta = 3 * np.pi / 2
                distance = 0
                while distance < self.environment.room_map.BOX_SIZE:
                    distance += 1

                    x = x_map + distance * math.cos(theta)
                    y = y_map + distance * math.sin(theta)

                    if self.environment.in_object(x, y):
                        found_wall = True
                        x = x_map + (distance - 1) * math.cos(theta)
                        y = y_map + (distance - 1) * math.sin(theta)
                        theta = np.pi / 2
                        break

            placements.append(Placement(line_sensors[index], pose=Pose(x, y, theta)))

        return PlacementResult(graph=graph, placements=placements)
