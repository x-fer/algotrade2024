import yaml
import os
import re

path_matcher = re.compile(r'\$\{([^}^{]+)\}')


def path_constructor(loader, node):
    value = node.value
    match = path_matcher.match(value)
    env_var = match.group()[2:-1]
    val = os.environ.get(env_var, None)
    if value[match.end():]:
        return val + value[match.end():]
    return val


yaml.add_implicit_resolver('!path', path_matcher)
yaml.add_constructor('!path', path_constructor)

with open("config.yaml", "r") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    config["in_tests"] = False

if config['log_networth_delay'] is None:
    config['log_networth_delay'] = 1