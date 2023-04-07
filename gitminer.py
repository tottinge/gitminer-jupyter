from collections import Counter
from datetime import datetime
from itertools import combinations
from typing import NamedTuple

import networkx as nx
from git import Repo, Commit

little_labels = dict(with_labels=True, font_size=7)
medium_labels = dict(with_labels=True, font_size=7)


def graph_file_to_file(git_repo):
    graph = nx.Graph()
    for current_commit in git_repo.iter_commits():
        file_combos = combinations(current_commit.stats.files, 2)
        for (left, right) in file_combos:
            if (left, right) in graph.edges:
                data = graph.get_edge_data(left, right)
                data['count'] = data.get('count', 1) + 1
            else:
                graph.add_edge(left, right,
                               count=1,
                               timestamp=current_commit.committed_datetime,
                               hash=current_commit.binsha)
    return graph


class CommitNode(NamedTuple):
    hash: str
    message: str
    timestamp: datetime


def graph_commit_to_file(repo):
    graph = nx.DiGraph()
    commit: Commit
    for commit in repo.iter_commits():
        item = CommitNode(commit.hexsha, commit.message, commit.committed_datetime)
        for filename in commit.stats.files:
            graph.add_edge(item, filename)
    return graph


# Organize commit data into structures in nx
repo = Repo("quizzology")
repo_graph = graph_file_to_file(repo)
commit_graph = graph_commit_to_file(repo)


# Most commonly committed files
def count_commits(commit_to_file_graph):
    return Counter(
        name
        for name, _ in commit_to_file_graph.edges
    )


file_commits = count_commits(commit_graph)
print("Most common commits (top 10):")
for filename, count in file_commits.most_common()[:10]:
    print(f'{filename}: {count}')
