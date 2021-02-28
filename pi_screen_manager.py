import logging
import time as sleeper
from datetime import datetime

import schedule
from ft5406 import Touchscreen, TS_PRESS, TS_RELEASE, TS_MOVE, Touch
from rpi_backlight import Backlight

from brightness_screen_manager import BrightnessScreenManager
from config import Config
from day_night_cycle import DayNightCycle, PeriodDay
from light_sensor import LightSensor
from luminosity_manager import LuminosityManager
from touch_manager import TouchManager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("main")

config = Config()

if not config.exists():
    config.write()
else:
    config.read()

backlight = Backlight()


def save_brightness_changed(brightness):
    period_day = day_night_cycle.period_day(datetime.now().time())
    if period_day == PeriodDay.DAY:
        config.data.brightness_day = brightness
    elif period_day == PeriodDay.EVENING:
        config.data.brightness_night = brightness
    config.write()


day_night_cycle = DayNightCycle()

brightness_manager = BrightnessScreenManager(backlight)
brightness_manager.brightness_changed.subscribe(on_next=save_brightness_changed)
lum_man = LuminosityManager(LightSensor(), brightness_manager, day_night_cycle)

if day_night_cycle.period_day(datetime.now().time()) == PeriodDay.NIGHT:
    logger.debug("is night set power off screen")
    brightness_manager.power_off()

day_night_cycle.night.subscribe(on_next=lambda x: brightness_manager.power_off())

touch_manager = TouchManager(brightness_manager)


def touch_handler(event, t: Touch):
    if event == TS_PRESS and t.slot == 1:
        logger.debug("Got Press %s, %s", t.position, t.slot)
        touch_manager.start(t.slot)
    if event == TS_MOVE and t.slot == 1:
        touch_manager.move(t)
    if event == TS_RELEASE and t.slot == 1:
        logger.debug("Got release %s, %s", t.position, t.slot)
        touch_manager.close(t.slot)


ts = Touchscreen()

for touch in ts.touches:
    touch.on_press = touch_handler
    touch.on_release = touch_handler
    touch.on_move = touch_handler

ts.run()

logger.debug("loop")
logger.info('%s', __name__)
while True:
    try:
        schedule.run_pending()

        sleeper.sleep(1)
    except:
        logger.debug("except")
        raise
