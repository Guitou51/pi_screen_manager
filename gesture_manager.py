import logging

import moosegesture
from rx.core.typing import Observer
from rx.subject import Subject


class GestureManager(Observer):

    logger = logging.getLogger("GestureManager")

    def __init__(self):
        self.gestures = []

    def on_error(self, error: Exception) -> None:
        pass

    def on_completed(self) -> None:
        self.gestures = []
        pass

    def on_next(self, value) -> None:
        self.move(value)
        pass

    brighter: Subject
    less_bright: Subject

    def move(self, point):
        self.gestures.append(point)
        gesture = moosegesture.getGesture(self.gestures)
        logging.debug("gesture: %s, %s", gesture, point)
        pass


    def __del__(self):
        del self.gestures