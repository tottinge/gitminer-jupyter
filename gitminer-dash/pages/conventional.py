import re
from collections import Counter
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
from dash import html, register_page, callback, Output, Input
from dash.dash_table import DataTable
from dash.dcc import Graph
from pandas import DataFrame

import data

register_page(__name__)

color_choices = {
    "feat": "rgb(141,211,199)",
    "ci": "rgb(255,255,179)",
    "fix": "rgb(251,128,114)",
    "chore": "rgb(190,186,218)",
    "build": "rgb(128,177,211)",
    "docs": "rgb(253,180,98)",
    "test": "rgb(179,222,105)",
    "refactor": "rgb(252,205,229)",
    "unknown": "rgb(188,128,189)",
}

layout = html.Div(
    [
        html.H2(
            id="id-conventional-h2",
            children="Change Type by Conventional Commit Messages"
        ),
        html.Button(
            id="id-conventional-refresh-button",
            children="Refresh"
        ),
        Graph(id="id-conventional-graph"),
        DataTable(
            id="id-conventional-table",
            columns=[{"name": i, "id": i} for i in ["file", "reason", "count"]],
            data=[]
        ),
    ]
)


@callback(
    [
        Output("id-conventional-table", "data"),
        Output("id-conventional-graph", "figure")
    ],
    Input("id-conventional-refresh-button", "n_clicks")
)
def update_conventional_table(n_clicks):
    dataframe = prepare_data()
    return dataframe.to_dict("records"), make_figure(dataframe)


conventional_commit_match_pattern = re.compile(r'^(\w+)[!(:]')
categories = {"build", "chore", "ci", "docs", "feat", "fix", "merge", "perf", "refactor", "revert", "style", "test"}


def prepare_data() -> DataFrame:
    # this is all just pasted in from cells in a python notebook
    # It's hideous, but we can fix that.

    # This would be more generally useful by date than file. When one clicks on a
    # bar for a given date, expanding to a list of files like this might
    # be useful.

    start = datetime.now().astimezone() - timedelta(weeks=52)
    commit_set = data.commits_in_period(start, datetime.now().astimezone())

    counter = Counter()
    for commit in commit_set:
        match = conventional_commit_match_pattern.match(commit.message)
        intent = "unknown"
        if match and match.group(1) in categories:
            intent = match.group(1)
        for filename in commit.stats.files.keys():
            counter[(filename, intent)] += 1

    most_changed_counter = Counter()
    for (filename, _), count in counter.items():
        most_changed_counter[filename] += count
    file_set = {file for file, reason in most_changed_counter.most_common(30)}

    data_source = [
        (filename, reason, value)
        for ((filename, reason), value) in counter.items()
        if filename in file_set
    ]
    df = pd.DataFrame(data_source, columns=["file", "reason", "count"])
    print(df)
    return df


def make_figure(df: DataFrame):
    """
    we're not using this yet, but will when we have the data working
    as we want it.
    """
    return px.bar(
        df,
        height=500,
        x="file",
        y="count",
        color="reason",
        color_discrete_map=color_choices
    )
