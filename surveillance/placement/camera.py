from typing import List

import numpy as np

from surveillance.environment import Environment
from surveillance.sensors.base import Sensor, SensorType
from surveillance.placement.step import PlacementStep, PlacementResult, Placement
from surveillance.helpers import Pose, compute_angle, node_to_px


class CameraSensorPlacement(PlacementStep):
    def __init__(self, environment: Environment):
        super().__init__(environment)

    def _compute_coverage(self, camera, pose, room):
        """
        Computes area inside given room that is covered by given camera sensor
        with particular placement (Assumes the placement is inside the room)
        Outputs list of covered nodes, the length of which is the covered area!
        """

        covered_nodes = []
        for node in room:
            # First compute the coordinates of the node in pixel space
            px, py = node_to_px(self.environment.room_map.graph[node]['pos'],
                                self.environment.room_map.BOX_SIZE)

            # Then check if point is covered by camera
            if camera.is_inside_viewcone(pose, px, py) == True:
                covered_nodes.append(node)

        return covered_nodes

    def place(self, sensors: List[Sensor], original_graph: dict) -> PlacementResult:
        """
        Place camera sensors in the environment. The process by which they are placed
        works as follows:

        > Cameras are always placed inside rooms, and only in corners of the rooms, as
          these are strictly always better than room edges or midpoints.

        1. Find the room with largest (unsurveiled) area
        2. Compute the coverage of placing a camera on each of that rooms corners
           Where the camera faces towards the average position of the room
        3. Select the corner with the highest coverage and place camera there
        4. Reduce the (unsurveiled) area of the room by the coverage of the camera
        5. Repeat until no cameras left to place

        The graph is not modified except for the new area values. This helps indicate to
        robot step what rooms (despite being large) are already mostly covered by cameras
        (The area now represents unsurveiled area, or leftover area, because the robot
        gains no value from checking rooms that are already covered by other sensors)
        """

        # Unpakc graphs from RoomMap object
        G = self.environment.room_map.graph
        M = self.environment.room_map.reduced_graph

        #TODO: First sort the camera list by coverage, to ensure cameras with
        #      best coverage get placed first

        placements = []

        for camera in sensors:

            # Find room with largest unsurveiled area (and sort rooms by unsurveiled area)
            area_node_pairs = [(node, M[node]['area']) for node in M if M[node]['type'] == 'room']
            area_node_pairs.sort(key=lambda x : x[1], reverse=True) # Sort by area
            room = area_node_pairs[0][0] # Select largest area and pick node

            # For all corners in room, measure coverage of camera placement and pick highest
            best_coverage = []
            best_pose = Pose(-1, -1, 0)
            chosen_room = -1
            # Iterate through rooms, biggest to smallest to find the best placement:
            for room_pair in area_node_pairs:
                room = room_pair[0]
                for corner in M[room]['corners']:
                    if G[corner]['raw_type'] != 'corner_cvx': # Exclude non-ideal convex corners
                        x_pos = G[corner]['pos'][0]
                        y_pos = G[corner]['pos'][1]

                        # Compute camera placement angle (aiming towards room centroid)
                        x_avg = M[room]['pos'][0]
                        y_avg = M[room]['pos'][1]
                        theta = compute_angle(x_pos, y_pos, x_avg, y_avg)

                        # Measure coverage and track the corner with the highest value
                        px, py = node_to_px(tuple([x_pos, y_pos]),
                                            self.environment.room_map.BOX_SIZE)
                        pose = Pose(x=px, y=py, theta=theta)
                        room_nodes = M[room]['room_nodes']
                        coverage = self._compute_coverage(camera, pose, room_nodes)
                        if len(coverage) > len(best_coverage):
                            best_coverage = coverage
                            best_pose = pose
                            chosen_room = room

            # Once the best placement is found, place camera there, and update room area
            placements.append(Placement(camera, pose=best_pose))
            M[chosen_room]['area'] -= len(best_coverage) # This way the 'area' of the room is
                                                         # only the unsurveiled area (useful)
            for covered_node in best_coverage:
                M[chosen_room]['room_nodes'].remove(covered_node) # Nodes can only be covered once

        return PlacementResult(graph=M, placements=placements)
