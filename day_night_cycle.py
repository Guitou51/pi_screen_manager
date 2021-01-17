import logging
from datetime import time, timedelta, datetime, date
from enum import Enum
import schedule
from rx.subject import Subject


class PeriodDay(Enum):
    DAY = 'DAY'
    EVENING = 'EVENING'
    NIGHT = 'NIGHT'


class DayNightCycle:
    logger = logging.getLogger("DayNightCycle")
    is_night: bool = False

    day_time = time(7, 0, 0)
    evening_time = time(18, 00, 0)
    night_time = time(23, 59, 59)
    midnight = time(0, 0, 0)
    one_second = timedelta(seconds=1)

    sunrise = Subject()
    sunset = Subject()
    night = Subject()

    def do_sunrise(self):
        self.sunrise.on_next(PeriodDay.DAY)

    def do_sunset(self):
        self.sunset.on_next(PeriodDay.EVENING)

    def do_nigth(self):
        self.night.on_next(PeriodDay.NIGHT)

    def __init__(self):
        schedule.every().day.at(self.day_time.strftime("%H:%M")).do(self.do_sunrise)
        schedule.every().day.at(self.evening_time.strftime("%H:%M")).do(self.do_sunset)
        schedule.every().day.at(self.night_time.strftime("%H:%M")).do(self.do_nigth)

    def period_day(self, current_time: time) -> PeriodDay:
        if self.day_time <= current_time < self.evening_time:
            return PeriodDay.DAY
        elif self.evening_time <= current_time < self.night_time:
            return PeriodDay.EVENING
        else:
            return PeriodDay.NIGHT

    def is_day(self, current_time: time) -> bool:
        dt = datetime.combine(date.today(), self.night_time) - self.one_second
        return self.day_time < current_time < dt.time()

    def __del__(self):
        self.sunrise.on_completed()
        self.sunset.on_completed()
        del self.sunrise
        del self.sunset
