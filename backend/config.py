import yaml
import os


with open("config.yaml", "r") as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)

config['testing'] = os.environ.get('TESTING', False)
