import argparse
import yaml
from typing import List
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
    fig, ax = plt.subplots()

    # Parse the config
    config = yaml.load(args.config, Loader=yaml.Loader)

    # Create the environment
    pixel_to_cm = config['environment']['map']['pixel_to_cm']
    environment = Environment(config['environment']['map']['image'])
    environment.display(ax)

    # Construct the various sensors
    sensors: List[Sensor] = []
    sensor_factory = SensorFactory(pixel_to_cm)
    for sensor_config in config['sensors']:
        sensors.append(sensor_factory.construct(sensor_config))

    # Determine the ideal positions
    for sensor in sensors:
        # TODO: Remove hard coded value
        sensor.place(350, 200, 0)

    # Loop over, updating the state
    plt.show()


if __name__ == '__main__':
    main()
