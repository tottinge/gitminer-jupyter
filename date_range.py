import unittest
from datetime import datetime, timedelta
from typing import NamedTuple


class DateRange(NamedTuple):
    start_time: datetime
    end_time: datetime

    @classmethod
    def last30d(cls):
        return DateRange()


class MyTestCase(unittest.TestCase):
    def test_something(self):
        period = DateRange.last30d()
        expected_start = datetime.today().astimezone() - timedelta(days=30)
        self.assertEqual(expected_start, period.start_time)  # add assertion here


if __name__ == '__main__':
    unittest.main()
