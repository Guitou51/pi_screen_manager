import logging

from ft5406 import Touch
from rx import operators
from rx.subject import Subject

from brightness_manager import BrightnessManager


class TouchManager:
    logger = logging.getLogger("TouchManager")

    the_subject = {}
    is_started = {}
    a = []


    def __init__(self, brightness_manager: BrightnessManager):
        self.brightness_manager = brightness_manager

    def start(self, _id):
        if _id not in self.is_started:
            self.is_started[_id] = False

        if not self.is_started[_id]:

            self.the_subject[_id] = Subject()

            def accumulator(acc, x):
                acc.append(x)
                return acc


            self.the_subject[_id].pipe(operators.map(lambda p: (p.x, p.y)),
                                       operators.scan(accumulator, seed=[])).subscribe(self.brightness_manager)

            self.is_started[_id] = True

    def move(self, t: Touch):
        if t.slot in self.is_started and self.is_started[t.slot]:
            self.the_subject[t.slot].on_next(t)

    def close(self, _id):
        self.is_started[_id] = False
        del self.is_started[_id]
        if _id in self.the_subject:
            self.the_subject[_id].on_completed()
            del self.the_subject[_id]

