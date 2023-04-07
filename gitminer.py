from collections import Counter
from datetime import datetime
from itertools import combinations
from git import Repo
import networkx as nx

repo = Repo("quizzology")

little_labels = dict(with_labels=True, font_size=7)
medium_labels = dict(with_labels=True, font_size=7)

repo_graph = nx.Graph()
for commit in repo.iter_commits():
    for (left, right) in combinations(commit.stats.files, 2):
        if (left, right) in repo_graph.edges:
            data = repo_graph.get_edge_data(left, right)
            data['count'] = data.get('count', 1) + 1
        else:
            repo_graph.add_edge(left, right,
                                count=1,
                                timestamp=commit.committed_datetime,
                                hash=commit.binsha)

from typing import NamedTuple


class CommitNode(NamedTuple):
    hash: str
    message: str
    timestamp: datetime


commit_graph = nx.DiGraph()
for commit in repo.iter_commits():
    item = CommitNode(commit.hexsha, commit.message, commit.committed_datetime)
    for file in commit.stats.files:
        commit_graph.add_edge(item, file)

file_commits = Counter()
for (commit, file) in commit_graph.edges:
    file_commits[file] += 1

print(file_commits.most_common()[:10])
