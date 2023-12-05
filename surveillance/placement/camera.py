from typing import List

import numpy as np

from surveillance.environment import Environment
from surveillance.sensors.base import Sensor, SensorType
from surveillance.placement.step import PlacementStep, PlacementResult, Placement
from surveillance.helpers import Pose


class CameraSensorPlacement(PlacementStep):
    def __init__(self, environment: Environment):
        super().__init__(environment)

    def _compute_angle(self, x1, y1, x2, y2):
        """
        Finds the counterclockwise angle of the line going from x1, y1, to x2, y2
        (In radians)
        """

        dx = x2 - x1 # > cosine(theta)
        dy = y2 - y1 # > sine(theta)

        theta = np.arctan2(dy/dx)

        return theta

    def _compute_coverage(self, camera, pose):
        """
        Computes area of
        """

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

            # Find room with largest unsurveiled area
            area_node_pairs = [(node, M[node]['area']) for node in M if 'area' in M[node]]
            area_node_pairs.sort(key=lambda x : x[1]) # Sort by area
            largest_room = area_node_pairs[-1] # Select largest area

            # For all corners in room, measure coverage of camera placement and pick highest
            best_coverage = 0
            best_pose = Pose(-1, -1, 0)
            for corner in M[largest_room]['corners']:
                x_pos = G[corner]['pos'][0]
                y_pos = G[corner]['pos'][1]

                # Compute camera placement angle (aiming towards room centroid)
                x_avg = M[largest_room]['pos'][0]
                y_avg = M[largest_room]['pos'][1]
                theta = self._compute_angle(x_pos, y_pos, x_avg, y_avg)

                # Measure coverage and track the corner with highest value
                pose = Pose(x=x_pos, y=y_pos, theta=theta)
                room_nodes = M[largest_room][]
                coverage = self._compute_coverage(camera, pose, room_nodes)
                if coverage > best_coverage:
                    best_coverage = coverage
                    best_pose = pose

            # Once best placement is found, place camera there, and update room area
            placements.append(Placement(camera, pose=best_pose))
            M[largest_room]['area'] -= best_coverage # This way the 'area' of the room is
                                                     # only the unsurveiled area (useful)

        return PlacementResult(graph=M, placements=placements)
