import cv2
import matplotlib.pyplot as plt
from matplotlib.axes._axes import Axes
from typing import List
import numpy as np

from surveillance.adversary import Adversary


class VornoiGraph:
    """
    Represents the minimum graph with each point representing a safe
    location a robot can move to. The robot can in a straight line each
    the nearies point on the graph safely.
    """
    def __init__(self, map: np.ndarray, cm_to_pixel: float):
        self.map = map
        print(np.max(self.map))

        self.cm_to_pixel = cm_to_pixel

        # Determine the contours
        self.contours, _ = cv2.findContours(
            self.map, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in self.contours:
            print('he')
        # Visualize the contours
        cv2.drawContours(self.map, self.contours, -1, (0, 255, 0), 10)
        # cv2.imshow('Contours', self.map)
        cv2.waitKey(0)

    def display(self, ax: Axes) -> None:
        """
        Display contours on the map
        """
        # ax.imshow(self.map)


class Environment:
    """
    Represents the area in which the surveillance is taking place. The
    environment is represented as a bitmap with pixel values with a "1"
    representing an occupied space and pixels with values of "0" being
    empty space.
    """
    def __init__(self, map_file: str, pixel_to_cm: float,
                 advisaries: List[Adversary]):

        image = cv2.imread(map_file)

        # Detect all edges in the image, and extend those edges to the border
        # of the image
        edges = cv2.Canny(image, 100, 200)

        lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)

        extended_lines = np.zeros_like(image)
        for line in lines:
            rho, theta = line[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho

            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))

            cv2.line(extended_lines, (x1, y1), (x2, y2), 255, 1)

        lines = cv2.HoughLines(edges, 1, np.pi / 270, 100)

        for line in lines:
            rho, theta = line[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho

            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))

            cv2.line(extended_lines, (x1, y1), (x2, y2), 255, 1)


        cv2.imshow('Edges', extended_lines)
        cv2.imshow('Original', edges)
        cv2.waitKey(0)


        # Open up the map and convert the pixel values to values of 0 and 1
        image_original = cv2.imread(map_file, cv2.IMREAD_GRAYSCALE)
        image_gray = cv2.threshold(image_original, 127, 255,
                                   cv2.THRESH_BINARY)[1]
        self.map = image_gray / 255

        self.advisaries = advisaries

        self.cm_to_pixel = 1 / pixel_to_cm

        self.graph = VornoiGraph(image_gray, self.cm_to_pixel)

    def display(self, ax: Axes) -> None:
        """
        Display the map of the environment
        """
        ax.imshow(self.map, cmap=plt.cm.gray)
        self.graph.display(ax)

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

    def in_adversary(self, x: float, y: float) -> bool:
        """
        Check if a given point is within an adversary
        """
        for adversary in self.advisaries:
            if adversary.in_adversary(x, y):
                return True
        return False
