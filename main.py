import argparse
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import yaml

from surveillance.adversary import Adversary, AdversaryPool
from surveillance.environment import Environment
from surveillance.sensors.base import Sensor
from surveillance.sensors.factory import SensorFactory
from surveillance.placement.placement import Placement


def main():
    parser = argparse.ArgumentParser(description='''Tool for viewing surveillance
                                     configurations virtually''')
    parser.add_argument('config', type=argparse.FileType('r'), help='''Config
                        file to load surveillance settings from''')
    args = parser.parse_args()

    # Setup the viewing
    fig, ax = plt.subplots()

    # Parse the config
    config = yaml.load(args.config, Loader=yaml.Loader)

    pixel_to_cm = config['environment']['map']['pixel_to_cm']
    max_timesteps = config['environment'].get('max_timesteps', np.inf)

    # Create the environment
    environment = Environment(config['environment']['map']['image'],
                              pixel_to_cm,
                              config['environment']['map']['graph'])

    # Pull in the test adversaries
    adversaries: List[Adversary] = []
    for adversary_config in config['adversaries']:
        adversaries.append(Adversary(pixel_to_cm, adversary_config,
                                     environment))

    # Create adversary pool
    adversary_pool = AdversaryPool(adversaries)

    # Construct the various sensors
    sensors: List[Sensor] = []
    sensor_factory = SensorFactory(pixel_to_cm, environment)
    for sensor_config in config['sensors']:
        sensors.append(sensor_factory.construct(sensor_config))

    # Determine the ideal positions
    placer = Placement(environment)
    placements = placer.get_placement(sensors)

    for placement in placements.placements:
        # TODO: Remove hard coded value
        print(placement.pose)
        placement.sensor.place(placement.pose.x, placement.pose.y, placement.pose.theta)

    for adversary in adversaries:
        adversary.place(350, 210, 0)

    # Simulation loop
    timestep = 0
    while timestep < max_timesteps:
        print('Timestep: {}'.format(timestep))
        plt.cla()
        # for stopping simulation with the esc key.
        plt.gcf().canvas.mpl_connect(
            'key_release_event',
            lambda event: [exit(0) if event.key == 'escape' else None])

        # Display the environment
        environment.display(ax)

        # Visualize the sensors
        for sensor in sensors:
            sensor.display(ax)

        # Visualize the adversaries
        for adversary in adversaries:
            adversary.display(ax)

        # Detect adversaries
        for sensor in sensors:
            if sensor.adversary_detected(adversary_pool):
                print('Adversary detected by sensor {}'.format(
                    sensor.name))

        # Update sensors
        for sensor in sensors:
            sensor.update()

        # Update adversaries
        for adversary in adversaries:
            adversary.update()

        # Update loop
        plt.pause(0.0001)
        timestep += 1

    plt.show()


if __name__ == '__main__':
    main()
