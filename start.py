import logging
import time as sleeper
from datetime import datetime

import schedule
from ft5406 import Touchscreen, TS_PRESS, TS_RELEASE, TS_MOVE, Touch
from rpi_backlight import Backlight
from rx.core import typing

from brightness_manager import BrightnessManager
from config import Config
from day_night_cycle import DayNightCycle

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
    if day_night_cycle.is_day(datetime.now().time()):
        config.data.brightness_day = brightness
    else:
        config.data.brightness_night = brightness
    config.write()


brightness_manager = BrightnessManager(backlight)
brightness_manager.brightness_changed.subscribe(on_next=save_brightness_changed)

day_night_cycle = DayNightCycle()

if day_night_cycle.is_day(datetime.now().time()):
    backlight.brightness = config.data.brightness_day
else:
    backlight.brightness = config.data.brightness_night

day_night_cycle.sunset.subscribe(on_next=lambda x: brightness_manager.brightness(config.data.brightness_night))
day_night_cycle.sunrise.subscribe(on_next=lambda x: brightness_manager.brightness(config.data.brightness_day))

touch_manager = TouchManager(brightness_manager)


def touch_handler(event, t: Touch):
    if event == TS_PRESS and t.slot == 1:
        logger.debug("Got Press %s, %s",t.position, t.slot)
        touch_manager.start(t.slot)
    if event == TS_MOVE and t.slot == 1:
        # print("Got move", t.position, t.slot)
        touch_manager.move(t)
    if event == TS_RELEASE and t.slot == 1:
        logger.debug("Got release %s, %s",t.position, t.slot)
        touch_manager.close(t.slot)

class Disposer:
    disposable: typing.Disposable = None

    def do_dipose(self) -> None:
        if self.disposable is not None:
            self.disposable.dispose()
            del self.disposable

    def is_disposed(self) -> bool:
        return self.disposable is None


ts = Touchscreen()

for touch in ts.touches:
    touch.on_press = touch_handler
    touch.on_release = touch_handler
    touch.on_move = touch_handler

ts.run()

while True:
    schedule.run_pending()

    sleeper.sleep(1)
