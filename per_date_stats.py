from collections import Counter
from datetime import datetime
from statistics import mean
from typing import Optional

import pandas


def report_commits_per_day(json_file, *, after: datetime = None, before: datetime = None):
    """
    I suspect that this can be done entirely in Pandas, but
    not knowing how, I fell back on Counter() to count the
    number of commits per day.
    """
    p = pandas.read_json(json_file)
    conditional = conditional_range(after, before)

    counts = Counter(d.date() for d in pandas.to_datetime(p['date'], utc=True) if conditional(d))

    print("Commits per day (UTC days)")
    for key, value in counts.items():
        print(f"    {key}: {value}")

    raw_values = counts.values()
    print(f"Max: {max(raw_values)}, Mean: {mean(raw_values)}, Min: {min(raw_values)}")


if __name__ == '__main__':
    report_commits_per_day('miner.json')


def if_version_of_conditional_range(low_value: Optional[datetime], high_value: Optional[datetime]):
    if low_value is None and high_value is None:
        return lambda x: True
    if low_value is None and high_value is not None:
        return lambda x: x < high_value.astimezone()
    if low_value is not None and high_value is None:
        return lambda x: x > low_value.astimezone()
    return lambda x: low_value.astimezone() < x < high_value.astimezone()


def dictionary_version(low_value: Optional[datetime], high_value: Optional[datetime]):
    selector = (low_value is not None, high_value is not None)
    choices = {
        (False, False): lambda x: True,
        (True, False): lambda x: x > low_value.astimezone(),
        (False, True): lambda x: x < high_value.astimezone(),
        (True, True): lambda x: low_value.astimezone() < x < high_value.astimezone()
    }
    return choices[selector]


def matching_conditional_range(early: Optional[datetime], late: Optional[datetime]):
    match (early, late):
        case (None, None):
            return lambda x: True
        case (start_date, None):
            return lambda x: x > start_date.astimezone()
        case (None, end_date):
            return lambda x: x < end_date.astimezone()
        case (start_date, end_date):
            return lambda x: start_date.astimezone() < x < end_date.astimezone()


conditional_range = matching_conditional_range
