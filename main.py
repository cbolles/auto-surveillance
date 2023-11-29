import argparse
import yaml
from typing import List
from surveillance.adversary import Adversary
from surveillance.environment import Environment
from surveillance.sensors.base import Sensor
from surveillance.sensors.factory import SensorFactory
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(description='''Tool for viewing surveillance
                                     configurations virtually''')
    parser.add_argument('config', type=argparse.FileType('r'), help='''Config
                        file to load surveillance settings from''')
    args = parser.parse_args()

    # Setup the viewing
    _, ax = plt.subplots()

    # Parse the config
    config = yaml.load(args.config, Loader=yaml.Loader)

    pixel_to_cm = config['environment']['map']['pixel_to_cm']

    # Pull in the test adversaries
    adversaries: List[Adversary] = []
    for adversary_config in config['adversaries']:
        adversaries.append(Adversary(pixel_to_cm, adversary_config))

    # Create the environment
    environment = Environment(config['environment']['map']['image'],
                              pixel_to_cm, adversaries)

    # Construct the various sensors
    sensors: List[Sensor] = []
    sensor_factory = SensorFactory(pixel_to_cm, environment)
    for sensor_config in config['sensors']:
        sensors.append(sensor_factory.construct(sensor_config))

    # Determine the ideal positions
    for sensor in sensors:
        # TODO: Remove hard coded value
        sensor.place(318, 200, 0)

    for adversary in adversaries:
        adversary.place(350, 211)

    # TODO: Add in update loop

    # Display the setup
    environment.display(ax)
    for sensor in sensors:
        sensor.display(ax)
    for adversary in adversaries:
        adversary.display(ax)
    for sensor in sensors:
        if sensor.advisary_detected():
            print('Adversary detected by sensor')

    plt.show()


if __name__ == '__main__':
    main()
