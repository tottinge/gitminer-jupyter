#!python3
import logging
from datetime import datetime, timedelta

import pandas
import pandas as pd
import typer
from git import Repo
from typing_extensions import Annotated

from .associative_modularity import strongest_pairs_by_ranking

app = typer.Typer()
logger = logging.getLogger(__name__)


def process_tags(repo: Repo) -> dict[str, str]:
    """Maps tag names to commit hashes"""
    from datetime import datetime
    result = dict()
    for tag_ref in repo.tags:
        if not tag_ref:
            logger.warning("No tag found")
            # Sometimes they're ill-formed somehow.
            continue
        if not tag_ref.tag:
            logger.warning("Lightweight tag %s", tag_ref)
            # I know, it makes no sense, but sometimes they don't.
            continue
        if not tag_ref.commit:
            logger.warning("There is no commit for tag %s", tag_ref)
            # Nearly as weird as the above two cases
            continue
        tagged_date = datetime.fromtimestamp(tag_ref.commit.committed_date)
        print(f"{tag_ref}, date {tagged_date}, summary {tag_ref.commit.summary}")
        result[tag_ref.commit.hexsha] = tag_ref.name
    return result


def intervals(repo: Repo, pattern: str):
    source = ((tag_ref.name, tag_ref.commit.authored_datetime) for tag_ref in repo.tags)
    raw_df = pd.DataFrame(data=source, columns=["name", "timestamp"])
    # Order by date rather than alphabetically by label
    raw_df = raw_df.sort_values(by=["timestamp"])
    # Limit to labels matching releases
    filter_bools = raw_df["name"].str.match(pattern)
    filtered_df = raw_df[filter_bools]
    # Have pandas calculate and insert the intervals
    filtered_df['interval'] = filtered_df['timestamp'].diff()
    return filtered_df


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
    source: Repo = Repo(repo_path)
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
    from .per_date_stats import report_commits_per_day
    report_commits_per_day(json_file, after=after, before=before)


@app.command("strongest-pairs")
def strongest_ranked_pairs(json_file: str):
    """
    Strongest-related pairs based on commits

    Lists the strength of the relationship, the count of co-commits, and the file names.
    """
    print("Strongest-pairs")
    strong_pairs = strongest_pairs_by_ranking(pandas.read_json(json_file))
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


if __name__ == "__main__":
    app()
