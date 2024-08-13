import os
import statistics
from collections import Counter, defaultdict
from collections.abc import Mapping
from itertools import combinations
from typing import Any, Iterable

import networkx as nx
import pandas
from networkx import Graph
from pandas import DataFrame


def strongest_pairs_by_ranking(commit_history: DataFrame):
    connection_rankings = calculate_relative_strengths(commit_history)
    pairing_count: Counter = count_combinations(commit_history)
    ranked_list_of_pairs = ((value, pair, pairing_count[pair])
                            for pair, value in connection_rankings.items())
    strong_pairs = sorted(ranked_list_of_pairs, reverse=True)
    return strong_pairs


def count_combinations(p: DataFrame) -> Counter:
    return Counter(
        pair
        for files in p['files']
        for pair in combinations([file['filename'] for file in files], 2)
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
        commit_files = [x['filename'] for x in files]
        if len(commit_files) < 1:
            continue
        for pair in combinations(commit_files, 2):
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


def calculate_relative_strengths(commit_df: DataFrame) -> defaultdict:
    """
    collect filenames from commit history, and calculate
    cumulative relative strength of connections between them.

    For a single commit, the strength of the connection is 1/len(files),
    > for only two files were committed, the strength is 0.5 (very high)
    > for 10 files in the commit then it's 0.1
    > for 100 files in the commit, the strength is 0.01
    If the files appeared together in each of the commits given above,
    then the strength of connection is .61 (quite high).

    @return: dict of (file,file):strength
    """
    assert 'files' in commit_df.columns
    result = defaultdict(float)
    for files in commit_df['files']:
        strength = (1.0 / len(files)) if files else 0
        filenames = [x['filename'] for x in files]
        for pair in combinations(filenames, 2):
            result[pair] += strength
    return result


def print_neighbors_list(commit_df: pandas.DataFrame, limit=10):
    print("Super-connectors' neighbors")
    graph = create_graph_from_dataframe(commit_df)
    for (_, filename) in list_super_connectors(commit_df)[:limit]:
        print(filename)
        for n in graph.neighbors(filename):
            print(f"    {n}")


def create_weighted_graph_from(source: Iterable[tuple[str, str, int | float]]) -> nx.Graph:
    graph: Graph = nx.Graph()
    graph.add_weighted_edges_from(source)
    return graph


def groupings(json_source, since_date=None) -> Iterable[tuple[str, str, float]]:
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


def tight_groupings(json_source: str, since_date: str = None):
    def dir_reversed(x):
        seperator = os.sep
        return seperator.join(reversed(x.split(seperator)))

    for number, grouping in enumerate(groupings(json_source, since_date)):
        print(f"Group {number}:")
        for member in sorted(grouping, key=dir_reversed):
            print("    ", member)


def main():
    # associative_groupings('website.json')
    all_of_it = pandas.read_json('miner.json')
    this_year = all_of_it.query('"2023-01-01" < date')
    print("Super-connectors")
    for (connections, filename) in list_super_connectors(this_year):
        print("    ", filename)


if __name__ == '__main__':
    main()
