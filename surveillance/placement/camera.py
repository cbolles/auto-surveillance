from typing import List, Tuple
import copy
import math

import numpy as np

from surveillance.environment import Environment
from surveillance.sensors.base import Sensor, SensorType
from surveillance.placement.step import PlacementStep, PlacementResult, Placement


class LineSensorPlacement(PlacementStep):
    def __init__(self, environment: Environment):
        super().__init__(environment)

    def place(self, sensors: List[Sensor], original_graph: dict) -> PlacementResult:
        """
        Place camera sensors in the environment. The process by which they are placed
        works as follows:

        > Cameras are always placed inside rooms, and only in corners of the rooms, as
          these are strictly always better than room edges or midpoints.

        1. Find the room with largest (unsurveiled) area
        2. Compute the coverage of placing a camera on each of that rooms corners
           Where the camera faces towards the average position of the room
        3. Select the corner with highest coverage and place camera there
        4. Reduce the (unsurveiled) area of the room by the coverage of the camera
        5. Repeat until no cameras left to place

        The graph is not modified save for the new area values. This helps indicate to
        robot step what rooms (despite being large) are already mostly covered by cameras
        """

        # Unpakc graphs from RoomMap object
        G = self.environment.room_map.graph
        M = self.environment.room_map.reduced_graph

        # Find room with largest unsurveiled area

        #return PlacementResult(graph=graph, placements=placements)
