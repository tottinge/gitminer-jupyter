"""
Extract a git repo to JSON for analysis in a document database
"""
import json

from git import Repo, Commit


def dump_it(source: Repo):
    commit: Commit
    print("[")
    for commit in source.iter_commits():  # Just get it all
        d = dict(
            hash=commit.hexsha,
            author=commit.author.name,
            coauthors=[a.name for a in commit.co_authors],
            date=str(commit.committed_datetime),
            message=commit.message,
            files=commit.stats.files,
            totals=commit.stats.total
        )
        print(json.dumps(d), ',')
    print("]")

if __name__ == '__main__':
    dump_it(Repo('../api'))
