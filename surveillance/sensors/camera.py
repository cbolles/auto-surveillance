from surveillance.sensors.base import Sensor, SensorType
from matplotlib.axes._axes import Axes
from matplotlib import patches
from surveillance.environment import Environment
from surveillance.adversary import AdversaryPool
import numpy as np
from typing import Tuple
from surveillance.helpers import compute_angle


class CameraSensor(Sensor):
    def __init__(self, pixel_to_cm: float, environment: Environment, config):
        super().__init__(pixel_to_cm, environment, config, SensorType.CAMERA)

        self.fov = config.get('field_of_view', 45)
        self.range = config.get('range', np.inf)

        DEG_PER_RAY = 3

        # Number of rays for raytracing depends on fov (rounded up)
        self.num_rays = int(np.ceil(self.fov / DEG_PER_RAY))

        self.fov = self.fov * np.pi/180 # Convert deg to rad

    def is_inside_viewcone(self, pose, px, py):
        """
        Returns true if given point (in pixel coordinates) is inside
        the view cone of the camera (DOES NOT CHECK VISIBILITY)
        """

        # For point to be inside viewcone, it has to be within the FOV angle
        # and has to be at a distance from the camera smaller than its max range
        cx = pose.x
        cy = pose.y
        theta = pose.theta

        # Check range (faster, so done first)
        distance = np.sqrt((px - cx)**2 + (py - cy)**2)
        if distance > self.range:
            return False

        # Check FOV cone
        max_angle = theta + self.fov/2 # If angle to point exceeds this, point is outside the cone
        min_angle = theta - self.fov/2 # If angle to point is below this, point is outside the cone
        angle_to_point = compute_angle(cx, cy, px, py)
        if (angle_to_point < min_angle) or (angle_to_point > max_angle):
            return False

        return True

    def _get_endpoint(self, theta) -> Tuple[float, float]:
        """
        Get the end points of the line originating at the camera at angle theta
        """
        if self.x is None or self.y is None or self.theta is None:
            raise Exception('Cannot display before sensor is placed')

        distance = 0
        self.next_x = self.x
        self.next_y = self.y

        while distance < self.range:
            distance += 1

            # Calculate the next point
            next_x = self.x + distance * np.cos(theta)
            next_y = self.y + distance * np.sin(theta)

            # Check if the next point is in the environment
            if not self.environment.in_environment(next_x, next_y):
                break

            # Check if the next point is in an object
            if self.environment.in_object(next_x, next_y):
                break

        return next_x, next_y

    def display(self, ax: Axes, color='b') -> None:
        if self.x is None or self.y is None or self.theta is None:
            raise Exception('Cannot display before sensor is placed')

        # USE THIS TO PLOT CONE LINES ONLY WITH COLLISION
        '''
        # Get fov cone end points
        end_x1, end_y1 = self._get_endpoint(self.theta-self.fov/2)
        end_x2, end_y2 = self._get_endpoint(self.theta+self.fov/2)

        # Plot the cone lines
        ax.plot([self.x, end_x1], [self.y, end_y1], 'b-')
        ax.plot([self.x, end_x2], [self.y, end_y2], 'b-')
        '''

        # OTHERWISE USE THIS TO PLOT ENTIRE CONE BOUNDARY
        # Plot the cone lines
        for angle in [self.theta - self.fov/2, self.theta + self.fov/2]:
            max_x = self.x + self.range * np.cos(angle)
            max_y = self.y + self.range * np.sin(angle)
            ax.plot([self.x, max_x], [self.y, max_y], str(color+'-'))
        # Plot cone arc
        arc = patches.Arc((self.x, self.y), self.range, self.range,
                          angle=self.theta, fill=False,
                          theta1=self.theta - self.fov/2, theta2=self.theta + self.fov/2)
        ax.add_patch(arc)

        # Plot a point at the start
        ax.plot(self.x, self.y, str(color+'o'))

    def adversary_detected(self, adversary_pool: AdversaryPool) -> bool:
        """
        Ray trace and determine if an adversary is detected
        """
        if self.x is None or self.y is None or self.theta is None:
            raise Exception('Cannot display before sensor is placed')

        for ray_angle in np.linspace(self.theta - self.fov/2, self.theta + self.fov/2,
                                     self.num_rays, endpoint=True):

            # Get ray endpoint and calculate ray length
            end_point_x, end_point_y = self._get_endpoint(ray_angle)
            length = np.sqrt((end_point_x - self.x)**2 + (end_point_y - self.y)**2)

            # Check in 1 cm increments from start point to end point
            for distance in np.arange(0, length, 1):
                # Calculate the next point
                next_x = self.x + distance * np.cos(ray_angle)
                next_y = self.y + distance * np.sin(ray_angle)

                # Check if the next point is in the adversary
                if adversary_pool.in_adversary(next_x, next_y):
                    return True

                distance += 1

        return False

    def update(self) -> None:
        """
        Camera doesn't update between time steps
        """
        pass
