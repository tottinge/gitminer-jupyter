import os
import statistics
from collections import Counter, defaultdict
from collections.abc import Mapping
from itertools import combinations
from statistics import mean, stdev
from typing import Any, Iterable

import networkx as nx
import pandas
from networkx import Graph
from pandas import DataFrame


def strongest_pairs_by_ranking(commit_history: DataFrame):
    connection_rankings = calculate_relative_strengths(commit_history)
    pairing_count: Counter = count_combinations(commit_history)
    strong_pairs = sorted(((value, pair, pairing_count[pair])
                           for pair, value in connection_rankings.items())
                          , reverse=True)
    return strong_pairs


def count_combinations(p: DataFrame) -> Counter:
    return Counter(
        pair
        for files in p['files']
        for pair in combinations(files, 2)
    )


def create_graph_from_pair_mapping(pairings: Mapping[tuple[str, str], Any]) -> nx.Graph:
    graph = nx.Graph()
    source = (
        (*pair, count)
        for pair, count in pairings.items()
    )
    graph.add_weighted_edges_from(source)
    return graph


def create_graph_from_dataframe(history: DataFrame):
    source = []
    for files in history["files"]:
        if len(files) > 1:
            for pair in combinations(files.keys(), 2):
                source.append(pair)
    return nx.Graph(source)


def list_mega_commits(history: DataFrame):
    for (index, (hashcode, date, message, files)) in history[['hash', 'date', 'message', 'files']].iterrows():
        if len(files) > 100:
            yield index, len(files), hashcode, date, message


def list_super_connectors(history: DataFrame):
    graph = create_graph_from_dataframe(history)
    listed = [(neighbor_count, filename)
              for filename, neighbor_count in graph.degree]
    biggest_first = sorted(listed, reverse=True)
    return biggest_first[:20]


def calculate_relative_strengths(p: DataFrame) -> defaultdict:
    d = defaultdict(float)
    for files in p['files']:
        strength = (1.0 / len(files)) if files else 0
        for pair in combinations(files, 2):
            d[pair] += strength
    return d


# p = pandas.read_json('classdojo.json')
# --- limit to a date range and get some stats
# l = p.query('"2023-05-01" < date')
# from associative_modularity import *
# from statistics import mean, stdev
# pairs = strongest_pairs_by_ranking(l)
# mean(pairs.values())

# --- Focus on the strongest ranked pair ----
# bigs = [(pair, rank) for rank,pair in pairs if rank > 0.99]
# len(bigs), len(pairs)

# --- Maybe try with graphs ---
# import networkx as nx
# nx.Graph(bigs)
# g = nx.Graph()
# g.add_weighted_edges_from( (*pair,weight) for pair,weight in bigs)
# list(nx.connected_components(g))[:10]
# poop = strongest_pairs_by_ranking(l)
# poop[:10]
# for rank,pair in poop[:25]:
#     print(f"{rank:8.3f} {pair[0]} <-> {pair[1]}")

# --- A few of these files show up mighty frequently ---
# --- investigate their connections
# list(g.neighbors('src/models/marketplace/Class.ts'))
# list(g.neighbors('language/en/dojo.emails.json'))


def print_neighbors_list(frame: pandas.DataFrame, limit=10):
    print("Super-connectors' neighbors")
    gr = create_graph_from_dataframe(frame)
    for (_, filename) in list_super_connectors(frame)[:limit]:
        print(filename)
        for n in gr.neighbors(filename):
            print(f"    {n}")


def create_weighted_graph_from(source: Iterable[tuple[str, str, int | float]]) -> nx.Graph:
    graph: Graph = nx.Graph()
    graph.add_weighted_edges_from(source)
    return graph


def groupings(json_source, since_date=None) -> nx.Graph:
    full_set = pandas.read_json(json_source)
    chosen_set = full_set.query(f'"{since_date}" < date') if since_date else full_set
    print(f"From {chosen_set.date.min()} through {chosen_set.date.max()}")
    return significant_groups_from_df(chosen_set, explain=True)


def significant_groups_from_df(dataframe, explain=False) -> Iterable[tuple[str, str, float]]:
    weighted_set = calculate_relative_strengths(dataframe)
    maximum = max(weighted_set.values())
    average = statistics.mean(weighted_set.values())
    median = statistics.median(weighted_set.values())
    stdev = statistics.stdev(weighted_set.values())
    limit_of_interest = (maximum - average) / 5 + average
    if explain:
        print(f"Max = {maximum}")
        print(f"Min = {min(weighted_set.values())}")
        print(f"Mean = {average}")
        print(f"Median = {median}")
        print(f"Stdev = {stdev}")
        print(f"Limit of interest = {limit_of_interest}")
    source = (
        (first, second, weight)
        for (first, second), weight in weighted_set.items()
        if weight > limit_of_interest
    )
    return nx.connected_components(create_weighted_graph_from(source))


def tight_groupings(json_source, since_date=None):
    seperator = os.sep

    def dir_reversed(x):
        return seperator.join(reversed(x.split(seperator)))

    for number, grouping in enumerate(groupings(json_source, since_date)):
        print(f"Group {number}:")
        for member in sorted(grouping, key=dir_reversed):
            print("    ", member)


if __name__ == '__main__':
    # associative_groupings('website.json')
    all_of_it = pandas.read_json('miner.json')
    this_year = all_of_it.query('"2023-01-01" < date')
    print("Super-connectors")
    for (connections, filename) in list_super_connectors(this_year):
        print("    ", filename)
