"""
Extract early git repo to JSON for analysis in early document database
"""
import json

import typer
from git import Repo, Commit


def dump_it(source: Repo):
    commit: Commit
    print("[")
    for line_number, commit in enumerate(source.iter_commits()):  # Just get it all
        if line_number > 0:
            print(",")
        d = dict(
            hash=commit.hexsha,
            author=commit.author.name,
            coauthors=[a.name for a in commit.co_authors],
            date=commit.committed_datetime.isoformat(),
            message=commit.message,
            files=commit.stats.files,
            totals=commit.stats.total
        )
        print(json.dumps(d), end='')
    print("\n]")


def main(repo_path: str):
    """
    We need to set this up for 'typer' to do the command line parsing
    for us.

    Should we package this with its libraries as early utility we can share?
    Will use typer and git modules
    """
    dump_it(Repo(repo_path))


if __name__ == '__main__':
    typer.run(main)
