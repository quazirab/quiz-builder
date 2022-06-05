import os


def os_environment(key, default):
    try:
        return os.environ[key]
    except KeyError:
        return default
