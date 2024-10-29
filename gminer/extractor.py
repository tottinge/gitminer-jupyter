"""
Extract early git repo to JSON for analysis in early document database
"""
import json

import typer
from git import Repo, Commit


def emit_commit_records_as_json(repository: Repo):
    for line_number, commit in enumerate(repository.iter_commits()):
        original_files = commit.stats.files
        normalized_files = [
            {'filename': filename, **original_files[filename]}
            for filename in original_files
        ]
        new_record = dict(
            hash=commit.hexsha,
            author=commit.author.name,
            coauthors=[a.name for a in commit.co_authors],
            date=commit.committed_datetime.isoformat(),
            message=commit.message,
            files=normalized_files,
            totals=commit.stats.total
        )
        yield new_record


def dump_it(repository: Repo):
    commit: Commit

    # Workaround for Windows powershell encoding issues
    import os, sys
    if os.name == "nt":
        sys.stdout.reconfigure(encoding='utf-8')

    print("[")
    for line_number, record in enumerate(emit_commit_records_as_json(repository)):
        if line_number > 0:
            print(",")
        print(json.dumps(record), end='')
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
