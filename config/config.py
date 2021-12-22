import os

from config import ConfigManager

CONFIG_FILE_PATH = os.getcwd() + '/config/global_config.json'

global_config_manager = ConfigManager(CONFIG_FILE_PATH)
