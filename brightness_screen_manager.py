import logging
from typing import List

from rpi_backlight import Backlight
from rx.core.typing import Observer
from rx.subject import Subject


class BrightnessScreenManager(Observer):
    brightness_changed: Subject
    logger = logging.getLogger("BrightnessManager")

    def __init__(self, backlight: Backlight):
        self.backlight = backlight
        self.brightness_changed = Subject()

    def on_next(self, value: List) -> None:
        if len(value) > 1:
            diff = -(value[-2][1] - value[-1][1])
            diff___ = self.backlight.brightness - (diff * 0.4)
            if 0 <= diff___ <= 100:
                self.backlight.brightness = diff___
                self.logger.debug("brightness: %s", self.backlight.brightness)

    def on_error(self, error: Exception) -> None:
        self.logger.error("error", exc_info=error)

    def on_completed(self) -> None:
        self.brightness_changed.on_next(self.backlight.brightness)

    def set_brightness(self, value):
        self.backlight.power = True
        self.logger.debug("set brightness %s", value)
        self.backlight.brightness = value

    def power_off(self):
        self.logger.debug("power off")
        self.backlight.power = False

    def power_on(self):
        self.logger.debug("power on")
        self.backlight.power = True

    def __del__(self):
        self.brightness_changed.on_completed()
