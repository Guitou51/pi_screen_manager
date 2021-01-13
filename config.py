import json
import logging
import os

class ConfigData:
    def __init__(self, brightness_day=50, brightness_night=10):
        self.brightness_day = brightness_day
        self.brightness_night = brightness_night


class Config:
    logger = logging.getLogger("Config")
    data: ConfigData

    def __init__(self):
        self.data: ConfigData = ConfigData(50, 10)

    def exists(self) -> bool:
        return os.path.exists('config.json')

    def read(self):
        with open('config.json') as json_file:
            j = json.load(json_file)
            self.data = ConfigData(**j)
            return self.data

    def write(self):
        with open('config.json', 'w') as outfile:
            json.dump(self.data.__dict__, outfile)

