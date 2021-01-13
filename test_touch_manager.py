from unittest import TestCase

from rx import operators as ops
from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestTouchManager(TestCase):
    def test_start(self):
        self.fail()

    def test_move(self):
        self.fail()

    def test_close(self):
        self.fail()

    def test_sample_regular(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(230, 3), on_next(
            260, 4), on_next(300, 5), on_next(350, 6), on_next(380, 7), on_completed(390))

        def create():
            return xs.pipe(ops.sample(50))

        results = scheduler.start(create)
        assert results.messages == [on_next(250, 3), on_next(
            300, 5), on_next(350, 6), on_next(400, 7), on_completed(400)]
