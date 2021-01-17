import unittest
import datetime

from day_night_cycle import DayNightCycle, PeriodDay


class DayNightCycleTest(unittest.TestCase):
    day_night_cycle = DayNightCycle()

    def test_period_day_is_day_at_7am(self):
        current_time = datetime.time(7, 0)

        self.assertEqual(self.day_night_cycle.period_day(current_time), PeriodDay.DAY)

    def test_period_day_is_day_at_12am(self):
        current_time = datetime.time(12, 0)

        self.assertEqual(self.day_night_cycle.period_day(current_time), PeriodDay.DAY)

    def test_period_day_is_day_at_last_second(self):
        current_time = datetime.time(17, 59, 59)

        self.assertEqual(self.day_night_cycle.period_day(current_time), PeriodDay.DAY)

    def test_period_day_is_evening_at_6pm(self):
        current_time = datetime.time(18, 0)

        self.assertEqual(self.day_night_cycle.period_day(current_time), PeriodDay.EVENING)

    def test_period_day_is_night_at_11pm(self):
        current_time = datetime.time(23, 0)

        self.assertEqual(self.day_night_cycle.period_day(current_time), PeriodDay.NIGHT)

    def test_is_day(self):
        current_time = datetime.time(12, 34)

        self.assertTrue(self.day_night_cycle.is_day(current_time))

    def test_is_night(self):
        current_time = datetime.time(00, 34)

        self.assertFalse(self.day_night_cycle.is_day(current_time))


if __name__ == '__main__':
    unittest.main()
