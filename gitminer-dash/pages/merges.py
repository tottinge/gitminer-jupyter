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
        if (commit.committed_datetime > recent_date and len(commit.parents) > 1)
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
    print("Records:", result)
    return result


layout = html.Div(
    [
        html.H2("Merge Magnitudes"),
        html.Button(id="refresh-button", children="Refresh"),
        html.Div(id="merge-graph-container"),
    ]
)


@callback(
    Output("merge-graph-container", "children"),
    Input("refresh-button", "n_clicks"),
    running=[Output("refresh-button", "disabled"), True, False]
)
def update_merge_graph(n_clicks: int):
    print("clicks", n_clicks)
    if not n_clicks:
        return html.H3("press refresh to acquire graph")
    data_frame = prepare_dataframe()
    print(data_frame.columns)
    bar_chart_figure = px.bar(data_frame=data_frame, x="date", y="lines", color="files", hover_name="date",
                              hover_data=["files", "lines", "comment"])
    print(bar_chart_figure.to_json())
    return [dcc.Graph(figure=bar_chart_figure)]
