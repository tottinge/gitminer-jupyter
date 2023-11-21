from collections import Counter
from datetime import datetime
from statistics import mean

import pandas


def report_commits_per_day(json_file, *, after: datetime = None, before: datetime = None):
    """
    I suspect that this can be done entirely in Pandas, but
    not knowing how, I fell back on Counter() to count the
    number of commits per day.
    """
    p = pandas.read_json(json_file)
    filter = conditional_range(after, before)

    counts = Counter(d.date() for d in pandas.to_datetime(p['date'], utc=True) if filter(d))

    print("Commits per day (UTC days)")
    for key, value in counts.items():
        print(f"    {key}: {value}")

    raw_values = counts.values()
    print(f"Max: {max(raw_values)}, Mean: {mean(raw_values)}, Min: {min(raw_values)}")
    return p


if __name__ == '__main__':
    p = report_commits_per_day('miner.json')


def conditional_range(early, late):
    match (early, late):
        case (None, None):
            return lambda x: True
        case (start_date, None):
            return lambda x: x > start_date.astimezone()
        case (None, end_date):
            return lambda x: x < end_date.astimezone()
        case (start_date, end_date):
            return lambda x: start_date.astimezone() < x < end_date.astimezone()
