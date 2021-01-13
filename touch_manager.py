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

    def start(self, id):
        if id not in self.is_started:
            self.is_started[id] = False

        if not self.is_started[id]:

            self.the_subject[id] = Subject()

            def accumulator(acc, x):
                acc.append(x)
                return acc


            self.the_subject[id].pipe(operators.map(lambda p: (p.x, p.y)),
                                      operators.scan(accumulator, seed=[])).subscribe(self.brightness_manager)

            self.is_started[id] = True
        pass

    def move(self, t: Touch):
        if t.slot in self.is_started and self.is_started[t.slot]:
            self.the_subject[t.slot].on_next(t)
        pass

    def close(self, id):
        self.is_started[id] = False
        del self.is_started[id]
        if id in self.the_subject:
            self.the_subject[id].on_completed()
            del self.the_subject[id]
        pass

