import argparse
import yaml
from surveillance.environment import Environment
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
    environment = Environment(config['environment']['map']['image'])
    environment.display(ax)

    # Construct the various sensors

    # Loop over, updating the state
    plt.show()


if __name__ == '__main__':
    main()
