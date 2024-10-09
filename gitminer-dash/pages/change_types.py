import dash
import pandas as pd
import plotly.express as px
# Note: PyCharm tags these as invalid imports, but we run
# the app from the parent dir and these are okay.
from algorithms.change_series import change_series, change_name
from algorithms.sorted_commits import get_most_recent_tags
from dash import html, dcc
from dash.dash_table import DataTable
from data import get_repo

dash.register_page("Change Types", path="/")


def prepared_data_frame():
    repo = get_repo()

    last_20 = get_most_recent_tags(repo, 20)

    # Get the Date, Name, and counters for the most recent commit diffs
    categorized_commits = change_series(start=last_20[0], commit_refs=last_20)
    change_df = pd.DataFrame(categorized_commits)
    return change_df


layout = html.Div(
    [
        dcc.Graph(id="local_graph",
                  figure=px.bar(
                      data := prepared_data_frame(),
                      title=f"Change Types and Magnitudes Across Tags",
                      x="Name",
                      y=list(change_name.values()),
                      labels=["Added", "Deleted", "Modified", "Removed"],
                      hover_name="Name",
                      hover_data=["Date"],
                      text_auto='.2s'
                  )),
        html.Hr(),
        html.H2("Source Data"),
        DataTable(data=data.to_dict('records')),
    ]
)
