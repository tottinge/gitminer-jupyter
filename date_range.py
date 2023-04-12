import unittest
from datetime import datetime, timedelta, time
from typing import NamedTuple

FIXED_DATE = datetime(year=2020, month=8, day=10, hour=17, minute=15, second=10).astimezone()

LAST_SECOND = time(23, 59, 59)

FIRST_SECOND = time(0, 0, 0)


class DateRange(NamedTuple):
    start_time: datetime
    end_time: datetime

    @classmethod
    def last30d(cls, reference=None):
        reference = reference or datetime.today().astimezone()
        range_end = datetime.combine(reference.date(), LAST_SECOND).astimezone()
        back_then = reference - timedelta(days=30)
        range_start = datetime.combine(back_then.date(), FIRST_SECOND).astimezone()
        return DateRange(range_start, range_end)

    def includes(self, param: datetime):
        return self.start_time <= param <= self.end_time


class MyTestCase(unittest.TestCase):
    def test_start_is_today_before_midnight(self):
        period = DateRange.last30d()
        self.assertEqual(datetime.today().date(), period.end_time.date())
        self.assertEqual(LAST_SECOND, period.end_time.time())

    def test_30_days_ago_start(self):
        period = DateRange.last30d()
        expected_start = datetime.today().astimezone() - timedelta(days=30)
        self.assertEqual(expected_start.date(), period.start_time.date())
        self.assertEqual(FIRST_SECOND, period.start_time.time())

    def test_out_of_range(self):
        period = DateRange.last30d(reference=FIXED_DATE)
        self.assertFalse(period.includes(FIXED_DATE + timedelta(days=1)))
        self.assertFalse(period.includes(FIXED_DATE - timedelta(days=31)))

    def test_in_range(self):
        period = DateRange.last30d(reference=FIXED_DATE)
        self.assertTrue(period.includes(FIXED_DATE))
        self.assertTrue(period.includes(FIXED_DATE - timedelta(days=10)))
        self.assertTrue(period.includes(FIXED_DATE - timedelta(days=20)))
        self.assertTrue(period.includes(FIXED_DATE - timedelta(days=30)))
        late_tonight = datetime.combine(FIXED_DATE.date(), LAST_SECOND).astimezone()
        self.assertTrue(period.includes(late_tonight))


if __name__ == '__main__':
    unittest.main()
