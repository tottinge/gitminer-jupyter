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
        dcc.Graph(id="code-lines-graph")
    ]
)


@callback(
    Output("code-lines-graph", "figure"),
    Input("code-lines-refresh-button", "n_clicks"),
    prevent_initial_call=True,
    running=(Output('code-lines-refresh-button', 'disabled'), True, False)

)
def update_code_lines_graph(n_clicks: int):
    print("Starting update")
    end_date = datetime.today().astimezone()  # datetime.today().astimezone()
    start_date = end_date - timedelta(days=30)  # until_today - timedelta(days=90)

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
                commit.hexsha,
            )

    # Convert connected chains to begin/end pairs of dates
    rows = []
    stacker = SequenceStacker()
    for ix, chain in enumerate(nx.connected_components(graph)):
        nodelist = [graph.nodes[key] for key in chain]
        ordered = sorted(nodelist, key=lambda x: x['committed'])
        earliest, latest = ordered[0], ordered[-1]
        duration = latest['committed'] - earliest['committed']
        height = stacker.height_for([earliest['committed'], latest['committed']])
        rows.append(dict(
            first=earliest['committed'].isoformat(),
            last=latest['committed'].isoformat(),
            elevation=height,
            commits=len(chain),
            head=earliest['sha'],
            tail=latest['sha'],
            duration=duration.days
        ))

    df = DataFrame(
        rows,
        columns=['first', 'last', 'elevation', 'commits', 'head', 'tail', 'duration']
    )
    figure = px.timeline(
        data_frame=df,
        x_start="first",
        x_end="last",
        y="elevation",
        color="commits",
        title="Code Lines",
        hover_data={
            'first': True,
            'head': True,
            'last': True,
            'tail': True,
            'commits': True,
            'duration': True,
            'elevation': False,
        }
    )
    return figure
