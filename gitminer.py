from collections import Counter
from datetime import datetime
from itertools import combinations
from typing import NamedTuple

import networkx as nx
from git import Repo, Commit

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



def main():
    repo = Repo("quizzology")
    repo_graph = graph_file_to_file(repo)
    commit_graph = graph_commit_to_file(repo)
    print_most_connected(repo_graph)
    print_most_common_commits(commit_graph)


if __name__ == '__main__':
    main()
