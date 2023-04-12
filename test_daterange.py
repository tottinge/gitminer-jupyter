import unittest
from datetime import datetime, timedelta
from daterange import LAST_SECOND, FIRST_SECOND, DateRange

FIXED_DATE = datetime(year=2020, month=8, day=10, hour=17, minute=15, second=10).astimezone()


class DateRangeTest(unittest.TestCase):
    def test_start_is_today_before_midnight(self):
        period = DateRange.last30d()
        self.assertEqual(datetime.today().date(), period.end_time.date())
        self.assertEqual(LAST_SECOND, period.end_time.time())

    def test_30_days_ago_starts_at_midnight(self):
        period = DateRange.last30d()
        expected_start = datetime.today().astimezone() - timedelta(days=30)
        self.assertEqual(expected_start.date(), period.start_time.date())
        self.assertEqual(FIRST_SECOND, period.start_time.time())

    def test_out_of_range(self):
        period = DateRange.last30d(ending_on=FIXED_DATE)
        self.assertFalse(period.includes(FIXED_DATE + timedelta(days=1)))
        self.assertFalse(period.includes(FIXED_DATE - timedelta(days=31)))

    def test_in_range_inclusive(self):
        period = DateRange.last30d(ending_on=FIXED_DATE)
        self.assertTrue(period.includes(FIXED_DATE))
        self.assertTrue(period.includes(FIXED_DATE - timedelta(days=10)))
        self.assertTrue(period.includes(FIXED_DATE - timedelta(days=20)))
        self.assertTrue(period.includes(FIXED_DATE - timedelta(days=30)))
        late_tonight = datetime.combine(FIXED_DATE.date(), LAST_SECOND).astimezone()
        self.assertTrue(period.includes(late_tonight))


if __name__ == '__main__':
    unittest.main()
