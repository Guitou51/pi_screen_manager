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

    CONFIG_JSON = 'config.json'

    def __init__(self):
        self.data: ConfigData = ConfigData(50, 10)

    def exists(self) -> bool:
        return os.path.exists(self.CONFIG_JSON)

    def read(self):
        with open(self.CONFIG_JSON) as json_file:
            j = json.load(json_file)
            self.data = ConfigData(**j)
            self.logger.debug("data loading %s", self.data.__dict__)
            return self.data

    def write(self):
        self.logger.debug("write data %s", self.data.__dict__)
        with open(self.CONFIG_JSON, 'w') as outfile:
            json.dump(self.data.__dict__, outfile)
