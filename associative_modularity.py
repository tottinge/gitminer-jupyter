from collections import Counter, defaultdict
from itertools import combinations
from statistics import mean, stdev

import networkx as nx
import pandas
from pandas import DataFrame
from typing import Generator


def list_mega_commits(history: DataFrame):
    for (index, (hashcode, date, message, files)) in history[['hash', 'date', 'message', 'files']].iterrows():
        if len(files) > 100:
            yield index, len(files), hashcode, date, message


def list_super_connectors(history: DataFrame):
    graph = create_graph_from_dataframe(history)
    listed = [(neighbors, filename)
              for filename, neighbors in graph.degree]
    biggest_first = sorted(listed, reverse=True)
    return biggest_first[:20]


def associative_groupings(json_file):
    commit_history: DataFrame = pandas.read_json(json_file)

    print("Mega-commits")
    for line in list_mega_commits(commit_history):
        print(line)

    print("Super-connectors")
    for item in list_super_connectors(commit_history):
        print(item)


def count_combinations(p: DataFrame) -> Counter:
    commit_sizes = [len(files) for files in p['files']]
    arbitrary_limit = mean(commit_sizes) + stdev(commit_sizes)
    print(f"Arbitrary limit is {arbitrary_limit}")
    return Counter(
        pair
        for files in p['files']
        for pair in combinations(files, 2)
        if len(files) < arbitrary_limit
    )


def relative_strengths(p: DataFrame) -> defaultdict:
    d = defaultdict(float)
    for files in p['files']:
        strength = files and 1.0 / len(files) or 0
        for pair in combinations(files, 2):
            d[pair] += strength
    return d


def create_graph_from_dataframe(history: DataFrame):
    source = []
    for files in history["files"]:
        if len(files) > 1:
            for pair in combinations(files.keys(), 2):
                source.append(pair)
    return nx.Graph(source)


def create_graph_from_counter(pairings: Counter) -> nx.Graph:
    graph = nx.Graph()
    source = (
        (*pair, count)
        for pair, count in pairings.items()
    )
    graph.add_weighted_edges_from(source)
    return graph


if __name__ == '__main__':
    associative_groupings('website.json')
