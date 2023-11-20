from collections import Counter

import pandas
import typer


def count_files_in_commits(json_file: str, goal: int):
    """
    This counts things
    """
    p = pandas.read_json(json_file)
    counter = Counter()
    for files in p["files"]:
        counter.update(files.keys())
    print(f"TOP {goal} most committed files:")
    for filename, commits in counter.most_common(goal):
        print(f"  {commits}: {filename}")


if __name__ == '__main__':
    typer.run(count_files_in_commits)
