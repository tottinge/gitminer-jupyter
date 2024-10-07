from collections import Counter
from datetime import datetime, timedelta

import dash
import pandas as pd
import plotly.express as px
from dash import html, dcc
from git import Repo
from pandas import DataFrame

dash.register_page(__name__, path="/")


def create_tag_interval_df(repo: Repo, since: datetime) -> pd.DataFrame:
    source = ((tag_ref.name, tag_ref.commit.authored_datetime) for tag_ref in repo.tags)
    raw_df = pd.DataFrame(data=source, columns=["name", "timestamp"])
    if raw_df.empty:
        return raw_df
    raw_df["timestamp"] = pd.to_datetime(raw_df["timestamp"], utc=True)
    sorted_df = raw_df.sort_values(by=["timestamp"])
    graph_df = sorted_df[sorted_df['timestamp'] > since].copy()
    graph_df['interval'] = graph_df['timestamp'].diff()
    return graph_df


ninety_days = datetime.today().astimezone() - timedelta(days=90)


def collect_diff_counts(repo: Repo, graph_df: DataFrame):
    earlier_label = graph_df.iloc[0]['name']
    diff_counts = []
    for index, data in graph_df.iterrows():
        current_label = data['name']
        diffs = repo.commit(earlier_label).diff(current_label)
        diff_counts.append(len(diffs))
        earlier_label = current_label
    return diff_counts


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

    # # Collect the time between tags and diff countes
    # graph_df = create_tag_interval_df(repo, ninety_days)
    # graph_df['timestamp'] = pd.to_datetime(graph_df['timestamp'], utc=True)
    # graph_df['diff_counts'] = collect_diff_counts(repo, graph_df)

    # Get the most recent 20 tags
    by_date = lambda x: x.commit.authored_datetime
    sorted_tags = sorted(repo.tags, key=by_date)
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
