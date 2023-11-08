import sys
from collections import Counter, defaultdict
from itertools import combinations
from os.path import dirname

import networkx as nx

from gitminer import count_commits
from numstat_parser import read_all_commits

"""
This is pretty much a junk file that needs rewritten.
"""


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


def build_all_graphs_from_one_stream(source=sys.stdin):
    """
    This is a terrible function. Better: pass in a list of
    reporter/collectors, each receives a commit and a file list.
    This function gets simple: it just passes the stream's
    output to the collectors; the collectors get simple and
    straightforward.
    """
    file_counts = Counter()
    commits_to_file = nx.DiGraph()
    author_to_dir = Counter()
    for commit, files in read_all_commits(source):
        for filename in files:
            commits_to_file.add_edge(
                commit.hash,
                filename
            )
            author_to_dir[(commit.author, dirname(filename))] += 1
        if len(files) < 2:
            continue
        for left, right in combinations(files, 2):
            key = tuple(sorted([left, right]))
            file_counts[key] += 1
    return file_counts, commits_to_file, author_to_dir


def do_reporting():
    file_counts, commits_to_file, author_to_dir = build_all_graphs_from_one_stream()

    commit_counter = count_commits(commits_to_file)
    print("\nMost committed files")
    for (name, count) in commit_counter.most_common(10):
        print(f'    {name} ({count})')

    print("\nMost co-committed files")
    for (left, right), count in file_counts.most_common(20):
        print(f'    {left} {right} ({count})')

    print("\nDirectory to Author (experimental, with abuse potential)")
    accumulator = defaultdict(list)
    for (author, module_dir), count in author_to_dir.most_common(100):
        accumulator[module_dir].append(author)
    for (module_dir, authors) in sorted(accumulator.items()):
        print(f"./{module_dir}:")
        for author in sorted(authors):
            print(f"   {author}")

    print("\nHighly Correlated Groups")
    from statistics import mode, mean, stdev
    # once is a fluke, twice is a coincidence -- so ignore onesy/twosey
    raw_counts = [x for x in file_counts.values() if x > 2]
    # Find the outliers
    threshold = mean(raw_counts) + stdev(raw_counts)
    # Give a basis for our outputs...
    print(
        f"Threshold:{threshold}, mean: {mean(raw_counts)}, mode: {mode(raw_counts)}, stdev: {stdev(raw_counts)}, max: {max(raw_counts)}")
    notable = nx.Graph([pair for pair, count in file_counts.items() if count >= threshold])
    for index, group in enumerate(nx.connected_components(notable)):
        print(f"Group {index} of size {len(group)}")
        for file in group:
            print(f"   {file}")
    print()


if __name__ == '__main__':
    do_reporting()


def significant_connections(stream):
    """
    This seems to generate a meaningful list of maintenance-coupled
    components. Whether the connections are "sane" or not requires
    human intervention at this time.
    Likely, if the names of the directories are highly dissimilar,
    it may suggest bad coupling between modules, but that is still
    something that remains to be seen.
    """
    stream = stream or open('./ILSITE.6month.txt')
    ctr = Counter()
    for commit, files in read_all_commits(stream):
        for left, right in combinations(files, 2):
            ctr[left, right] += 1
    threshold = max(ctr.values()) / 3
    notable = nx.Graph([pair for pair, count in ctr.items() if count >= threshold])
    return list(nx.connected_components(notable))
