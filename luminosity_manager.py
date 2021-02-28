from datetime import datetime
from typing import List

from rx import operators

from brightness_screen_manager import BrightnessScreenManager
from day_night_cycle import DayNightCycle, PeriodDay
from light_sensor import LightSensor


class LuminosityManager:
    a = 0.06
    b = 5

    luminosity_table: List

    def __normalize(self, current, target):
        if target == current:
            return [current]
        gap = abs(current - target)
        # gap = gap / 4
        new_target = target
        coef = 1
        if target < current:
            new_target = current - gap
            coef = -1
        elif target > current:
            new_target = current + gap

        array = self.split_to_array(coef, current, new_target, 10)

        return array

    def split_to_array(self, coef, current, target, size_of_array):
        new_gap = abs(current - target)
        step = new_gap / (size_of_array - 1)

        array_ = []
        current_ = current
        for i in range(0, size_of_array):
            array_.append(current_)
            current_ = current_ + step * coef
        return array_

    def __init__(self, light_sensor: LightSensor, brightness_screen_manager: BrightnessScreenManager,
                 day_night_cycle=DayNightCycle):
        self.luminosity_table = []
        for i in range(65536):
            self.luminosity_table.append(self.a * i + self.b)

        self.brightness_screen_manager = brightness_screen_manager
        self.disposable = light_sensor.lumen.pipe(
            operators.filter(lambda x: day_night_cycle.period_day(datetime.now().time()) != PeriodDay.NIGHT),
            operators.map(lambda lx: int(self.__compute(lx))),
            operators.map(lambda b: min(b, 100)),
            operators.map(lambda b: self.__normalize(brightness_screen_manager.backlight.brightness, b)),
            operators.distinct_until_changed()).subscribe(
            on_next=lambda b: self.__set_brightness(b))

    def __compute(self, lx):
        return self.a * lx + self.b

    def __set_brightness(self, array):
        for i in array:
            self.brightness_screen_manager.set_brightness(i)
            # time.sleep(0.05)

    def __del__(self):
        self.disposable.dispose()
