import sys
from itertools import combinations

import networkx as nx

from gitminer import count_commits, count_connections
from numstat_parser import read_all_commits

commits_to_file = nx.DiGraph()
file_to_file = nx.Graph()

for commit, files in read_all_commits(sys.stdin):
    for filename in files:
        commits_to_file.add_edge(
            commit.hash,
            filename
        )
    if len(files) < 2:
        continue
    for left, right in combinations(files, 2):
        file_to_file.add_edge(left, right)

commit_counter = count_commits(commits_to_file)
print("\nMost committed files")
for (name, count) in commit_counter.most_common(10):
    print(f'    {name} ({count})')

print("\nMost file-to-file connections")
connections = count_connections(file_to_file)
for name, count in connections[:10]:
    print(f'    {name} ({count})')

print("\nConnected Groups")
groups = list(nx.connected_components(file_to_file))
print(f"There are {len(groups)} groups identified.")
for n, record in enumerate(groups):
    size = len(record)
    print(f"{len(record)} in group {n}")
    for file in list(record)[:10]:
        print(f"   {file}")
    if size > 10:
        print(f"     ... and {size - 10} more.")

big_groups = [ group for group in groups if len(groups) > 40]

