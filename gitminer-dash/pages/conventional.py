import re
from collections import Counter
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
from dash import html, register_page, callback, Output, Input
from dash.dash_table import DataTable
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
        html.H2(id="id-conventional-h2", children="This is the conventional page"),
        DataTable(id="id-conventional-table"),
    ]
)


@callback(
    Output("id-conventional-table", "data"),
    Input("id-conventional-table", "n_clicks")
)
def update_conventional_table(n_clicks):
    return [prepare_data().to_dict("records")]


conventional_commit_match_pattern = re.compile(r'^(\w+)[!(:]')
categories = {"build", "chore", "ci", "docs", "feat", "fix", "merge", "perf", "refactor", "revert", "style", "test"}


def prepare_data() -> DataFrame:
    # this is all just pasted in from cells in a python notebook
    # It's hideous, but we can fix that.

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

    return df


def make_figure(df: DataFrame):
    figure = px.bar(df,
                    x="file",
                    y="count",
                    color="reason",
                    color_discrete_map=color_choices)
