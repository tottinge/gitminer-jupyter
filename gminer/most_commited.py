from collections import Counter

import typer

from gminer.types import FilesEntry
from gminer.utility import read_git_history_from_file


def count_files_in_commits(json_file: str, goal: int):
    """
    This counts things
    """
    p = read_git_history_from_file(json_file)
    counter = Counter()
    for files in p.files:
        f: FilesEntry = files
        counter.update(x['filename'] for x in f)
    print(f"TOP {goal} most committed files:")
    for filename, commits in counter.most_common(goal):
        print(f"  {commits}: {filename}")


if __name__ == '__main__':
    typer.run(count_files_in_commits)
