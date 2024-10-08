#!python3
import logging
import os
import re
from collections import Counter
from datetime import datetime, timedelta
from os.path import isdir, isfile
from statistics import mean

import git
import git.repo.fun
import pandas as pd
import typer
from typing_extensions import Annotated

import gminer.types
from gminer.utility import read_git_history_from_file
from .associative_modularity import strongest_pairs_by_ranking

app = typer.Typer()
logger = logging.getLogger(__name__)


@app.command("release-freq")
def release_frequency(path_to_repo: str, tag_regex: str) -> None:
    repo = git.Repo(path_to_repo)
    df: pd.DataFrame = release_tag_intervals(repo, tag_regex)
    timings: pd.Series = df.interval
    print(f"Max {timings.max()}\nMin {timings.min()}\nMean: {timings.mean()}")

    # draw a picture
    import plotly.express as px
    from datetime import timedelta
    start = datetime.now().astimezone() - timedelta(days=90)
    recent_data = df[df['timestamp'] > start]
    figure = px.histogram(recent_data, x="timestamp", y="interval")
    figure.update_layout(bargap=0.2)
    figure.write_image("sample.png", format="png")


def release_tag_intervals(repo: git.Repo, pattern: str) -> pd.DataFrame:
    source = ((tag_ref.name, tag_ref.commit.authored_datetime.replace(minute=0, second=0, microsecond=0))
              for tag_ref in repo.tags)
    raw_df = pd.DataFrame(data=source, columns=["name", "timestamp"])
    if raw_df.empty:
        return raw_df
    # Order by date rather than alphabetically by label
    raw_df = raw_df.sort_values(by=["timestamp"])
    # Limit to labels matching releases
    filter_bools = raw_df["name"].str.match(pattern)
    filtered_df = raw_df[filter_bools].copy()
    # Have pandas calculate and insert the intervals
    filtered_df['interval'] = filtered_df['timestamp'].diff()
    filtered_df['days_since'] = filtered_df['interval'].dt.days
    return filtered_df


def releases_by_week_numbers(repo: git.Repo, year, pattern: str):
    release_pattern = re.compile(pattern)
    year_of = lambda x: x.commit.authored_datetime.isocalendar().year
    week_of = lambda x: x.commit.authored_datetime.isocalendar().week
    date_of = lambda x: x.commit.authored_datetime

    source = ((tag_ref.name, year_of(tag_ref), week_of(tag_ref), date_of(tag_ref))
              for tag_ref in repo.tags
              if tag_ref.commit.authored_datetime.year >= year and release_pattern.search(tag_ref.name))
    counts = Counter((year, week) for (_, year, week, _) in source)
    out_data = (
        (datetime.fromisocalendar(key[0], key[1], 1), releases)
        for (key, releases) in counts.items()
    )
    return pd.DataFrame(data=out_data, columns=["week", "releases"])


@app.command("most-committed")
def cli_most_committed(
        json_file: str,
        max_to_list: Annotated[int, typer.Option("--size", "-s")] = 5
):
    """
    List the files that have been committed the most often
    """
    from .most_commited import count_files_in_commits
    count_files_in_commits(json_file, max_to_list)


@app.command("extract-to-json")
def cli_extract_to_json(repo_path: str):
    """
    Extract the contents of early git repo to early json file
    """
    from .extractor import dump_it
    source: git.Repo = git.Repo(repo_path)
    dump_it(source)


@app.command("commits-per-day")
def daily_commits(
        json_file: str,
        after: Annotated[datetime, typer.Option("--after", "--early")] = None,
        before: Annotated[datetime, typer.Option("--before", "--late")] = None
):
    """
    List the total number of commits per day
    """
    from .per_date_stats import count_commits_per_day
    p = read_git_history_from_file(json_file)
    counts = count_commits_per_day(p, after=after, before=before)
    if not counts:
        print("No commits in range")
        return
    print("Commits per day (UTC days)")
    for key, value in counts.items():
        print(f"    {key}: {value}")
    raw_values = counts.values()
    print(f"Max: {max(raw_values)}, Mean: {mean(raw_values)}, Min: {min(raw_values)}")


@app.command("strongest-pairs")
def strongest_ranked_pairs(json_file: str):
    """
    Strongest-related pairs based on commits

    Lists the strength of the relationship, the count of co-commits, and the file names.
    """
    print("Strongest-pairs")
    strong_pairs = strongest_pairs_by_ranking(read_git_history_from_file(json_file))
    print("Strength Count  Pair")
    for value, (left, right), count in strong_pairs[:50]:
        print(f"{value:8.3f}:{count:5d} {left}\n               {right}\n")


@app.command("tightest-groupings")
def tightest_groupings(
        json_file: str,
        after: Annotated[datetime, typer.Option("--since")] = None
):
    """
    List the tightest groupings of source files.

    Groupings are defined by the frequency in which files were committed together.
    By default, the last 12 months are examined.
    """
    from .associative_modularity import tight_groupings
    since = after.date() if after else (datetime.now().date() - timedelta(weeks=52))
    tight_groupings(json_file, since.isoformat())


def analyze_and_report(source: str, destination: str):
    repo: git.Repo
    extract: gminer.types.GitHistoryDataframe

    if not isdir(source) and not isfile(source):
        raise ValueError(source, "not a dir or a repo extract file")
    if not isdir(destination):
        os.makedirs(destination)
    else:
        ...  # Empty or version existing files

    if isdir(source) and git.repo.fun.is_git_dir(source):
        ...  # do all the things we can do with a repo
    else:
        ...  # do all the


if __name__ == "__main__":
    app()
