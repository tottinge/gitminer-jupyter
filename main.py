import json
from collections import Counter

import pandas
import typer
from git import Repo, Commit

app = typer.Typer()


@app.command("most_committed")
def cli_most_committed(json_file: str, max_to_list: int):
    """
    List the files that have been committed the most often
    """
    p = pandas.read_json(json_file)
    counter = Counter()
    for files in p["files"]:
        counter.update(files.keys())
    print(f"TOP {max_to_list} most committed files:")
    for filename, commits in counter.most_common(max_to_list):
        print(f"  {commits}: {filename}")


@app.command("extract_to_json")
def cli_extract_to_json(repo_path: str):
    """
    Extract the contents of a git repo to a json file
    """
    source: Repo = Repo(repo_path)
    commit: Commit
    print("[")
    for line_number, commit in enumerate(source.iter_commits()):  # Just get it all
        if line_number > 0:
            print(",")
        d = dict(
            hash=commit.hexsha,
            author=commit.author.name,
            coauthors=[a.name for a in commit.co_authors],
            date=str(commit.committed_datetime),
            message=commit.message,
            files=commit.stats.files,
            totals=commit.stats.total
        )
        print(json.dumps(d), end='')
    print("\n]")


if __name__ == "__main__":
    app()
