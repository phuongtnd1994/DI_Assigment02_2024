import configparser
import os
config = configparser.ConfigParser(os.environ)
config.read('config.ini')

def get_config():
    return config.read('config.ini')