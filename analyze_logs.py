import sys
from collections import Counter
from itertools import combinations

import networkx as nx

from gitminer import count_commits, count_connections
from numstat_parser import read_all_commits


def build_weighted_file_graph(source=sys.stdin):
    weighted_file_to_file = nx.Graph()
    linkage_counter = Counter()
    for _, files in read_all_commits(source):
        for left, right in combinations(files, 2):
            linkage_counter[(left, right)] += 1
    for (edge, weight) in linkage_counter.items():
        weighted_file_to_file.add_edge(*edge, weight=weight)
    return weighted_file_to_file


def build_weighted_author_graph(source=sys.stdin):
    weighted_author_to_file = nx.Graph(name="authors")
    counter = Counter()
    for commit, files in read_all_commits(source):
        for file in files:
            counter[(commit.author, file)] += 1
    for edge, weight in counter.items():
        weighted_author_to_file.add_edge(*edge, weight=weight)
    return weighted_author_to_file


def build_graphs(source=sys.stdin):
    file_to_file = nx.Graph()
    commits_to_file = nx.DiGraph()
    for commit, files in read_all_commits(source):
        for filename in files:
            commits_to_file.add_edge(
                commit.hash,
                filename
            )
        if len(files) < 2:
            continue
        for left, right in combinations(files, 2):
            file_to_file.add_edge(left, right)
    return file_to_file, commits_to_file


def do_reporting():
    weighted_file_linkages = build_weighted_file_graph()
    file_to_file, commits_to_file = build_graphs()

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
    for n, group in enumerate(groups):
        size = len(group)
        print(f"{len(group)} in group {n}")
        for file in list(group)[:10]:
            print(f"   {file}")
        if size > 10:
            print(f"     ... and {size - 10} more.")

    print("\nEXPERIMENT")
    # Note - person-to-file or person-to-directory mappings?
    # Can we see who the frequent maintainers are for a given period?
    # Will this indicate contention?


if __name__ == '__main__':
    do_reporting()
