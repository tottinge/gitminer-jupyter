from collections import Counter
from datetime import datetime
from itertools import combinations
from typing import NamedTuple

import networkx as nx
from git import Repo, Commit

from daterange import DateRange

little_labels = dict(with_labels=True, font_size=7)
medium_labels = dict(with_labels=True, font_size=7)


def graph_file_to_file(git_repo, earliest=None, latest=None):
    earliest = earliest or datetime.fromtimestamp(0).astimezone()
    latest = latest or datetime.today().astimezone()
    graph = nx.Graph()
    for commit in git_repo.iter_commits():
        if not earliest <= commit.committed_datetime <= latest:
            continue
        file_combos = combinations(commit.stats.files, 2)
        for (left, right) in file_combos:
            if (left, right) in graph.edges:
                data = graph.get_edge_data(left, right)
                data['count'] = data.get('count', 1) + 1
            else:
                graph.add_edge(left, right,
                               count=1,
                               timestamp=commit.committed_datetime,
                               hash=commit.binsha)
    return graph


class CommitNode(NamedTuple):
    hash: str
    message: str
    timestamp: datetime


def graph_commit_to_file(repo, earliest=None, latest=None):
    earliest = earliest or datetime.fromtimestamp(0).astimezone()
    latest = latest or datetime.today().astimezone()
    graph = nx.DiGraph()
    commit: Commit
    for commit in repo.iter_commits():
        if not earliest <= commit.committed_datetime <= latest:
            continue
        item = CommitNode(commit.hexsha, commit.message, commit.committed_datetime)
        for filename in commit.stats.files:
            graph.add_edge(item, filename)
    return graph


# Most commonly committed files
def count_commits(commit_to_file_graph):
    return Counter(
        name
        for commit, name in commit_to_file_graph.edges
    )


def version_a(candidates, criteria):
    result = []
    for candidate in candidates:
        if criteria.passes(candidate):
            result.append(candidate)
    return result


def version_b(candidates, criteria):
    return [c for c in candidates if criteria.passes(c)]


def count_connections(file_to_file_graph):
    counted_connections = list(file_to_file_graph.degree())
    ordered = sorted(counted_connections, reverse=True, key=lambda x: x[1])
    return ordered


def print_most_common_commits(commit_to_file_graph):
    file_commits = count_commits(commit_to_file_graph)
    print("Most commits (top 10):")
    for filename, count in file_commits.most_common()[:10]:
        print(f'{filename}: {count}')


def print_most_connected(file_to_file_graph):
    ordered = count_connections(file_to_file_graph)
    print("Top ten most connected files")
    for filename, count in ordered[:10]:
        print(f'{filename} {count}')
    print()


def build_time_limited_commit_graph(original: nx.DiGraph, period: DateRange):
    commit: CommitNode
    filename: str
    return nx.DiGraph(
        (commit, filename)
        for (commit, filename) in original.edges
        if period.includes(commit.timestamp)
    )


def get_repo_commits_graph(repository_path):
    repo = Repo(repository_path)
    commit_graph = graph_commit_to_file(repo)
    return commit_graph


def main(repository_path):
    """
    This is a sketch area, nothing end-user useful.
    """
    repo = Repo(repository_path)
    # repo_graph = graph_file_to_file(repo)
    # print_most_connected(repo_graph)
    commit_graph = graph_commit_to_file(repo)
    print("Overall:")
    print_most_common_commits(commit_graph)

    print("Last 30 Days")
    desired_period = DateRange.last30d(datetime(2022, 9, 1, 12, 00, 23))
    time_limited = build_time_limited_commit_graph(commit_graph, desired_period)
    print_most_common_commits(time_limited)
    return commit_graph, time_limited


def file_pairings_from_commit_graph(commit_graph):
    for commit in commit_graph.nodes:
        neighbors = list(commit_graph.neighbors(commit))
        if not neighbors:
            continue
        for pairing in combinations(neighbors,2):
            yield pairing


# concept: file A and file B are neighbors;
# File A is committed with B 100 of 300 commits
# File B is committed with A 100 of 104 commits
# B is very tightly coupled to A.
# B is fairly coupled to B.
# If I edit B, I'd better consider A also!
# If I edit A, I might consider B.
# Should A and B probably be in the same module?
# with a multigraph of files called X, x[filename] yields an array of two-tuples,
# Where the first element is the related filename, and the second is a dict with one
# element per link that was added (the data is empty - we could add the commit to it?)
# So len(x[filename][filename]) is the number of commits.
#

if __name__ == '__main__':
    import typer

    typer.run(main)
