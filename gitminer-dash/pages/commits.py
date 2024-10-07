from collections import Counter

import dash
import pandas as pd
import plotly.express as px
from dash import html, dcc

dash.register_page(__name__, path="/")


def change_series(start, last_20):
    for tag in last_20:
        diffs = start.commit.diff(tag.commit)
        yield {
            'Date': start.commit.committed_datetime.date(),
            'Name': start.name,
            **Counter(change_name[x.change_type] for x in diffs)
        }
        start = tag


def prepared_data_frame():
    import data
    repo = data.get_repo(data.repository_path)

    # Get the most recent 20 tags
    sorted_tags = sorted(repo.tags, key=(lambda x: x.commit.authored_datetime))
    last_20 = sorted_tags[-20:]

    # Get the Date, Name, and counters for the most recent commit diffs
    change_df = pd.DataFrame(change_series(start=last_20[0], last_20=last_20))
    return change_df


change_name = {
    "A": "Files Added",
    "D": "Files Deleted",
    "R": "Files Renamed",
    "M": "Files Modified"
}

layout = html.Div(
    [
        html.H2("This is the commits page"),
        dcc.Graph(id="local_graph",
                  figure=px.bar(
                      poo := prepared_data_frame(),
                      title=f"Changes Across Tags",
                      x="Name",
                      y=list(change_name.values()),
                      labels=["Added", "Deleted", "Modified", "Removed"],
                      hover_name="Name",
                      hover_data=["Date"],
                      text_auto='.2s'
                  )),
    ]
)
