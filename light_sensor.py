import logging

import smbus
from rx import Observable, interval
from rx import operators

from bh1750 import BH1750


class LightSensor:
    logger = logging.getLogger("LightSensor")
    bus = smbus.SMBus(1)  # Rev 2 Pi uses 1
    sensor = BH1750(bus)

    lumen: Observable

    def __init__(self):
        self.sensor.set_sensitivity(254)
        self.sensor.cont_low_res()
        self.lumen = interval(0.25).pipe(operators.map(lambda x: self.sensor.get_result()))
