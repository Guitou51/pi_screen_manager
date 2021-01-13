import unittest
import datetime

from day_night_cycle import DayNightCycle


class DayNightCycleTest(unittest.TestCase):
    day_night_cycle= DayNightCycle()

    def test_is_day(self):
        current_time =datetime.time(12, 34)

        self.assertTrue(self.day_night_cycle.is_day(current_time))

    def test_is_night(self):
        current_time =datetime.time(00, 34)

        self.assertFalse(self.day_night_cycle.is_day(current_time))


if __name__ == '__main__':
    unittest.main()
