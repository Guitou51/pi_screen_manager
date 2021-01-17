import logging

import moosegesture
from rx.core.typing import Observer
from rx.subject import Subject


class GestureManager(Observer):
    logger = logging.getLogger("GestureManager")

    def __init__(self):
        self.gestures = []

    def on_error(self, error: Exception) -> None:
        self.logger.error('error on  gesture', exc_info=error)

    def on_completed(self) -> None:
        self.gestures = []

    def on_next(self, value) -> None:
        self.move(value)

    brighter: Subject
    less_bright: Subject

    def move(self, point):
        self.gestures.append(point)
        gesture = moosegesture.getGesture(self.gestures)
        logging.debug("gesture: %s, %s", gesture, point)

    def __del__(self):
        del self.gestures
