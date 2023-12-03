import cv2 as cv
import matplotlib.pyplot as plt
from matplotlib.axes._axes import Axes
from surveillance.roombuilder.roombuilder import RoomMap


class Environment:
    """
    Represents the area in which the surveillance is taking place. The
    environment is represented as a bitmap with pixel values with a "1"
    representing an occupied space and pixels with values of "0" being
    empty space.
    """
    def __init__(self, map_file: str, pixel_to_cm: float, graph_file: str):
        # Open up the map and convert the pixel values to values of 0 and 1
        image = cv.imread(map_file, cv.IMREAD_GRAYSCALE)
        image = cv.threshold(image, 127, 255, cv.THRESH_BINARY)[1]
        image = image / 255

        # Store the map
        self.map = image

        # Load the graph
        self.room_map = RoomMap.load(graph_file)

        self.cm_to_pixel = 1 / pixel_to_cm

    def display(self, ax: Axes) -> None:
        """
        Display the map of the environment
        """
        ax.imshow(self.map, cmap=plt.cm.gray)

    def in_environment(self, x: float, y: float) -> bool:
        """
        Check if a given point is within the bounds of the environment
        """
        x_coordinate = int(x * self.cm_to_pixel)
        y_coordinate = int(y * self.cm_to_pixel)
        return 0 <= x_coordinate < self.map.shape[1] and \
            0 <= y_coordinate < self.map.shape[0]

    def in_object(self, x: float, y: float) -> bool:
        """
        Check if a given point is within an object
        """
        x_coordinate = int(x * self.cm_to_pixel)
        y_coordinate = int(y * self.cm_to_pixel)
        return self.map[y_coordinate, x_coordinate] == 0
