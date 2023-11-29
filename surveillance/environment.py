import cv2 as cv
import matplotlib.pyplot as plt


class Environment:
    """
    Represents the area in which the surveillance is taking place. The
    environment is represented as a bitmap with pixel values with a "1"
    representing an occupied space and pixels with values of "0" being
    empty space.
    """
    def __init__(self, map_file: str):
        # Open up the map and convert the pixel values to values of 0 and 1
        image = cv.imread(map_file, cv.IMREAD_GRAYSCALE)
        image = cv.threshold(image, 127, 255, cv.THRESH_BINARY)[1]

        # Store the map
        self.map = image

    def display(self, ax) -> None:
        """
        Display the map of the environment
        """
        ax.imshow(self.map, cmap=plt.cm.gray)
