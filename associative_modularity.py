from collections import Counter
from itertools import combinations
from statistics import mean, stdev

import networkx as nx
import pandas
from pandas import DataFrame


def list_mega_compiles(history: DataFrame):
    for (index, (hash, date, message,files)) in history[['hash', 'date', 'message', 'files']].iterrows():
        if len(files) > 100:
            print(f"{index}, has {len(files)}, {date}, {message}")


def associative_groupings(json_file):
    p: DataFrame = pandas.read_json(json_file)

    g: nx.Graph = create_graph(count_combinations(p))

    print("pMaintenance Groups:")
    for each in nx.connected_components(g):
        if len(each) > 3:
            print(len(each))


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


def create_graph(pairings: Counter) -> nx.Graph:
    graph = nx.Graph()
    source = (
        (*pair, count)
        for pair, count in pairings.items()
    )
    graph.add_weighted_edges_from(source)
    return graph


if __name__ == '__main__':
    associative_groupings('website.json')
