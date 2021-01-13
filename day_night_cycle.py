import logging
from datetime import time, timedelta, datetime, date
from enum import Enum
import schedule
from rx.subject import Subject


class DayNight(Enum):
    DAY = 'DAY'
    NIGHT = 'NIGHT'


class DayNightCycle:
    logger = logging.getLogger("DayNightCycle")
    is_night: bool = False

    day_time = time(6, 0, 0)
    night_time = time(22, 00, 0)
    midnight = time(0, 0, 0)
    one_second = timedelta(seconds=1)

    sunrise = Subject()
    sunset = Subject()

    def __init__(self):
        schedule.every().day.at(self.day_time.strftime("%H:%M")).do(lambda: self.sunrise.on_next(None))
        schedule.every().day.at(self.night_time.strftime("%H:%M")).do(lambda: self.sunset.on_next(None))

    def is_day_or_night(self) -> DayNight:
        if self.is_day(datetime.now().time()):
            return DayNight.DAY
        else:
            return DayNight.NIGHT

    def is_day(self, current_time: time) -> bool:
        dt = datetime.combine(date.today(), self.night_time) - self.one_second
        return self.day_time < current_time < dt.time()

    def __del__(self):
        self.sunrise.on_completed()
        self.sunset.on_completed()
        del self.sunrise
        del self.sunset
