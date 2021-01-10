import logging
import os
import time as sleeper
from datetime import datetime, time, timedelta, date
from typing import List, Any

import moosegesture
import schedule
from ft5406 import Touchscreen, TS_PRESS, TS_RELEASE, TS_MOVE, Touch
from rpi_backlight import Backlight
from rx import operators
from rx.core import typing, GroupedObservable
from rx.core.typing import Observer
from rx.subject import Subject
import json

logging.basicConfig(level=logging.DEBUG)


class Config:
    def __init__(self):
        self._data = {'data': {'brightness': {'day': '50', 'night': '10'}}}

    def exists(self) -> bool:
        return os.path.exists('config.json')

    def read(self) -> Any:
        with open('config.json') as json_file:
            self._data = json.load(json_file)
            return self._data

    def write(self) -> None:
        with open('config.json', 'w') as outfile:
            json.dump(self._data, outfile)

    def data(self):
        return self._data

    pass


config = Config()

if not config.exists():
    config.write()
else:
    config.read()


class DayNightCycle:
    is_night: bool = False

    day_time = time(6, 0, 0)
    night_time = time(23, 30, 0)
    midnight = time(0, 0, 0)
    one_second = timedelta(seconds=1)

    def is_day(self, current_time: time = time()) -> bool:
        dt = datetime.combine(date.today(), self.night_time) - self.one_second
        return self.day_time < current_time < dt.time()

    pass


def power_off():
    logging.debug('power off')
    backlight.power = False


def power_off_is_night():
    if is_night:
        backlight.power = False


def power_on():
    logging.debug('power on')
    backlight.power = True


def on(observer, scheduler) -> None:
    power_on()
    observer.on_completed()


def off(observer, scheduler) -> None:
    power_off()
    observer.on_completed()


def sunrise() -> None:
    is_night = False
    power_on()


def sunset() -> None:
    is_night = True
    power_off()


class GestureManager(Observer):

    def __init__(self):
        self.gestures = []

    def on_error(self, error: Exception) -> None:
        pass

    def on_completed(self) -> None:
        self.gestures = []
        pass

    def on_next(self, value) -> None:
        # logging.debug("""GestureManager.on_next %s""", value)

        self.move(value)

        pass

    brighter: Subject
    less_bright: Subject

    def move(self, point):
        self.gestures.append(point)
        # iterator = list(map(lambda p: (p.x, p.y), points))
        # print(iterator)
        gesture = moosegesture.getGesture(self.gestures)
        logging.debug("gesture: %s, %s", gesture, point)
        pass

    def get_gesture(self, pts):
        return moosegesture.getGesture(pts)
        pass

    def __del__(self):
        # logging.debug("GestureManager.__del__")
        del self.gestures


class BrightnessManager(Observer):
    brightness_changed: Subject

    def __init__(self, backlight: Backlight):
        self.backlight = backlight
        self.brightness_changed = Subject()
        pass

    def on_next(self, value: List) -> None:
        if len(value) > 1:
            diff = -(value[-2][1] - value[-1][1])
            diff___ = self.backlight.brightness - (diff * 0.4)
            if 0 < diff___ < 100:
                self.backlight.brightness = diff___
                logging.debug("brightness: %s", self.backlight.brightness)
        pass

    def on_error(self, error: Exception) -> None:
        pass

    def on_completed(self) -> None:
        self.brightness_changed.on_next(self.backlight.brightness)
        pass

    def __del__(self):
        self.brightness_changed.on_completed()


class TouchManager:
    the_subject = {}
    is_started = {}
    gesture_manager = {}
    a = []

    def start(self, id1):
        if id1 not in self.is_started:
            self.is_started[id1] = False

        if not self.is_started[id1]:
            # interval(timedelta(seconds=1)).
            # source = from([1,2,3,4]);
            self.the_subject[id1] = Subject()
            self.gesture_manager[id1] = GestureManager()

            def accumulator(acc, x):
                acc.append(x)
                return acc

            self.the_subject[id1].pipe(operators.map(lambda p: (p.x, p.y)),
                                       operators.scan(accumulator, seed=[])).subscribe(BrightnessManager(backlight))
            # .subscribe(self.gesture_manager[id1])

            # self.the_subject.pipe(operators.group_by(lambda th: th.id, lambda th: th), operators.flat_map(
            #     lambda grp_obs: grp_obs.pipe(operators.map(lambda p: (p.x, p.y)))))\
            #     .subscribe(self.gesture_manager)

            # zip(self.the_subject.pipe(operators.map(lambda p: (p.x, p.y))),
            #     interval(timedelta(milliseconds=100))).subscribe(
            #     on_next=lambda x: self.gesture_manager.move(x),
            #     on_completed=lambda: logging.debug("complete"))

            #
            # self.the_subject \
            #     .pipe(operators.group_by(lambda th: th.id, lambda th: th),
            #           operators.flat_map(
            #               lambda grp: grp.pipe(operators.map(lambda p: (p.x, p.y)), operators.to_list()))) \
            #     .subscribe(on_next=lambda x: self.gesture_manager.move(x),
            #                on_completed=lambda: logging.debug("complete"))
            self.is_started[id1] = True
        pass

    def move(self, t: Touch):
        if t.slot in self.is_started and self.is_started[t.slot]:
            self.the_subject[t.slot].on_next(t)
        pass

    def close(self, id1):
        self.is_started[id1] = False
        del self.is_started[id1]
        if id1 in self.the_subject:
            self.the_subject[id1].on_completed()
            del self.the_subject[id1]
            g = self.gesture_manager[id1]
            del g
            del self.gesture_manager[id1]
        pass

    def select_obs(self, observer: GroupedObservable):
        print("select_obs", observer.key)
        return observer
        pass


touch_manager = TouchManager()


def touch_handler(event, t: Touch):
    if event == TS_PRESS and t.slot == 1:
        print("Got Press", t.position, t.slot)
        touch_manager.start(t.slot)
    if event == TS_MOVE and t.slot == 1:
        # print("Got move", t.position, t.slot)
        touch_manager.move(t)
    if event == TS_RELEASE and t.slot == 1:
        print("Got release", t.position, t.slot)
        touch_manager.close(t.slot)


backlight = Backlight()
backlight.brightness = 15
print(backlight.brightness)


# current_time = datetime.now().time()
# print("now =", current_time)
#
# dt = datetime.combine(date.today(), night_time) - one_second


# if day_time < current_time < dt.time():
#     power_on()
#     is_night = False
# if night_time < current_time < (
#         datetime.combine(date.today(), midnight) - one_second).time() or midnight < current_time < day_time:
#     power_off()
#     is_night = True
#
# schedule.every().day.at(day_time.strftime("%H:%M")).do(sunrise)
# schedule.every().day.at(night_time.strftime("%H:%M")).do(sunset)


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

    # for touch in ts.poll():
    #     # logging.debug('touch')
    #     if touch.valid and disposer.is_disposed():
    #         logging.debug('valid touch')
    #         observable_on = create(on)
    #         c = observable_on.pipe(operators.concat(timer(timedelta(seconds=5)), create(off)))
    #         # observable_wait = timer(timedelta(seconds=5))
    #         # observable_off = create(off)
    #
    #         disposable = c.subscribe(on_completed=lambda: disposer.do_dipose())
    #
    #         disposer.disposable = disposable
    #         logging.debug('after subscribe')

    # print(c)
    sleeper.sleep(1)
