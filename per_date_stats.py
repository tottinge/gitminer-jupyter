from collections import Counter
from statistics import mean

import pandas


def report_commits_per_day(json_file):
    """
    I suspect that this can be done entirely in Pandas, but
    not knowing how, I fell back on Counter() to count the
    number of commits per day.
    """
    p = pandas.read_json(json_file)
    counts = Counter(d.date() for d in pandas.to_datetime(p['date'], utc=True))

    print("Commits per day (UTC days)")
    for key, value in counts.items():
        print(f"    {key}: {value}")

    raw_values = counts.values()
    print(f"Max: {max(raw_values)}, Mean: {mean(raw_values)}, Min: {min(raw_values)}")
    return p


if __name__ == '__main__':
    p = report_commits_per_day('miner.json')
