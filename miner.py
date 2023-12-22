#!python3
from datetime import datetime, timedelta

import pandas
import typer
from git import Repo
from typing_extensions import Annotated

from associative_modularity import strongest_pairs_by_ranking

app = typer.Typer()


@app.command("most-committed")
def cli_most_committed(
        json_file: str,
        max_to_list: Annotated[int, typer.Option("--size", "-s")] = 5
):
    """
    List the files that have been committed the most often
    """
    from most_commited import count_files_in_commits
    count_files_in_commits(json_file, max_to_list)


@app.command("extract-to-json")
def cli_extract_to_json(repo_path: str):
    """
    Extract the contents of early git repo to early json file
    """
    from extractor import dump_it
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
    from per_date_stats import report_commits_per_day
    report_commits_per_day(json_file, after=after, before=before)


@app.command("strongest-pairs")
def strongest_ranked_pairs(json_file: str):
    """
    Strongest-related pairs based on commits
    """
    strong_pairs = strongest_pairs_by_ranking(pandas.read_json(json_file))
    for value, (left, right) in strong_pairs[:50]:
        print(f"{value:8.3f}: {left} {right}")


@app.command("tightest-groupings")
def tightest_groupings(
        json_file: str,
        after: Annotated[datetime, typer.Option("--since")] = None
):
    """
    List the tightest groupings of files based on maintenance
    since a given date (or 6 months ago if not specified)
    """
    from associative_modularity import tight_groupings
    since = after.date() if after else (datetime.now().date() - timedelta(weeks=52))
    tight_groupings(json_file, since.isoformat())


if __name__ == "__main__":
    app()

# Counter(d.date for d in pd.to_datetime(df['Date'])
