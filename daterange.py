from datetime import time, datetime, timedelta
from typing import NamedTuple

LAST_SECOND = time(23, 59, 59)
FIRST_SECOND = time(0, 0, 0)


class DateRange(NamedTuple):
    start_time: datetime
    end_time: datetime

    @classmethod
    def last30d(cls, ending_on=None):
        ending_on = ending_on or datetime.today().astimezone()
        range_end = datetime.combine(ending_on.date(), LAST_SECOND).astimezone()
        back_then = ending_on - timedelta(days=30)
        range_start = datetime.combine(back_then.date(), FIRST_SECOND).astimezone()
        return DateRange(range_start, range_end)

    def includes(self, param: datetime):
        return self.start_time <= param <= self.end_time
