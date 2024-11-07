from datetime import datetime, timedelta

import networkx as nx
import plotly.express as px
from dash import html, register_page, callback, Output, Input, dcc
from pandas import DataFrame

from data import commits_in_period
from .stacking import SequenceStacker

register_page(module=__name__, title="Code Lines")

layout = html.Div(
    [
        html.H2("Lines of Code"),
        html.Button(id="code-lines-refresh-button", children=["Refresh"]),
        dcc.Graph(id="code-lines-graph", figure={"data": []}),
        html.P(id="code-lines-description-1", children=[
            "In git, commits reference their parent. "
            "A code line is a series of single-parent "
            "(non-merge) commits where each one references the one before it."
        ]),
        html.P(id="code-lines-description-2", children=[
            "By examining code lines, we can see how much concurrent activity is taking place "
            "and if the developers commit often or seldom (relative to other code lines)."
        ])

    ]
)


@callback(
    Output("code-lines-graph", "figure"),
    Input("code-lines-refresh-button", "n_clicks"),
    running=(Output('code-lines-refresh-button', 'disabled'), True, False)

)
def update_code_lines_graph(n_clicks: int):
    days_duration = 30
    end_date = datetime.today().astimezone()  # datetime.today().astimezone()
    start_date = end_date - timedelta(days=days_duration)  # until_today - timedelta(days=90)

    # Make all the connections
    graph = nx.Graph()
    for commit in commits_in_period(start_date, end_date):
        if len(commit.parents) > 1:
            continue
        for parent in commit.parents:
            graph.add_node(
                parent.hexsha,
                committed=parent.
                committed_datetime,
                sha=parent.hexsha
            )
            graph.add_node(
                commit.hexsha,
                committed=commit.committed_datetime,
                sha=commit.hexsha
            )
            graph.add_edge(
                parent.hexsha,
                commit.hexsha
            )

    # Convert connected chains to begin/end pairs of dates
    rows = []
    stacker = SequenceStacker()

    chain_summary = []
    for chain in nx.connected_components(graph):
        nodelist = [graph.nodes[key] for key in chain]
        ordered = sorted(nodelist, key=lambda x: x['committed'])
        earliest, latest = ordered[0], ordered[-1]

        early_timestamp = earliest['committed']
        late_timestamp = latest['committed']

        duration = late_timestamp - early_timestamp
        commit_counts = len(chain)
        record = (early_timestamp, late_timestamp, commit_counts, duration, earliest, latest)

        chain_summary.append(record)

    for data in sorted(chain_summary):
        early_timestamp, late_timestamp, commit_counts, duration, earliest, latest = data
        height = stacker.height_for([early_timestamp, late_timestamp])
        rows.append(dict(
            first=early_timestamp.isoformat(),
            last=late_timestamp.isoformat(),
            elevation=height,
            commits=commit_counts,
            head=earliest['sha'],
            tail=latest['sha'],
            duration=duration.days,
            density=(duration.days) / commit_counts
        ))

    df = DataFrame(
        rows,
        columns=['first', 'last', 'elevation', 'commit_counts', 'head', 'tail', 'duration', 'density']
    )
    figure = px.timeline(
        data_frame=df,
        x_start="first",
        x_end="last",
        y="elevation",
        color="density",
        title=f"Code Lines (last {days_duration} days)",
        labels={
            "elevation": "",
            "density": "Commit Sparsity",
            "first": "Begun",
            "last": "Ended",
            "duration": "Days"
        },
        hover_data={
            'first': True,
            'head': True,
            'last': True,
            'tail': True,
            'commit_counts': True,
            'duration': True,
            'elevation': False,
            'density': True
        }
    )
    return figure
