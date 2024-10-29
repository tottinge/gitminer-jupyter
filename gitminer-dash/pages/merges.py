from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
from dash import register_page, html, dcc, callback, Output, Input

import data

register_page(__name__, title="Merge Sizes")


# Doing this synchronously here (called in the layout)
# makes startup time very slow.
def prepare_dataframe():
    repo = data.get_repo()
    recent_date = datetime.today().astimezone() - timedelta(days=30)
    recent_merges = [
        commit for commit in repo.iter_commits()
        if commit.committed_datetime > recent_date
           and len(commit.parents) > 1
    ]
    columns = [
        "hash",
        "date",
        "comment",
        "lines",
        "files"
    ]
    source = (
        (commit.hexsha,
         commit.committed_datetime.date(),
         commit.message,
         commit.stats.total["lines"],
         commit.stats.total["files"])
        for commit in recent_merges
    )
    result = pd.DataFrame(source, columns=columns).sort_values(by="date")
    return result


layout = html.Div(
    [
        html.H2("Merge Magnitudes"),
        html.Button(id="refresh-button", children="Refresh"),
        dcc.Store(id='merge-data', ),
        dcc.Graph(id="merge-graph"),
    ]
)


@callback(
    Output("merge-graph", "figure"),
    Input("refresh-button", "n_clicks")
)
def update_merge_graph(n_clicks: int):
    data_frame = prepare_dataframe()
    return px.bar(
        data_frame,
        x="date",
        y="lines",
        color="files",
        hover_name="date",
        hover_data=["files", "lines", "comment"]
    )
