from datetime import datetime, timedelta

import networkx as nx
import plotly.express as px
from dash import html, register_page, callback, Output, Input, dcc
from pandas import DataFrame

from data import commits_in_period

register_page(module=__name__, title="Code Lines")


@callback(
    Output("code-lines-graph", "figure"),
    Input("code-lines-refresh-button", "n_clicks"),
    running=[
        (Output("code-lines-refresh-button", "disabled"), True, False),
        (Output("code-lines-refresh-button", "children"), "Calculating", "Refresh")
    ],
    prevent_initial_call=True

)
def update_graph():
    end_date = datetime.today().astimezone()  # datetime.today().astimezone()
    start_date = end_date - timedelta(days=90)  # until_today - timedelta(days=90)

    graph = nx.Graph()
    for commit in commits_in_period(start_date, end_date):
        if len(commit.parents) > 1:
            continue
        for parent in commit.parents:
            graph.add_node(parent.hexsha, committed=parent.committed_datetime)
            graph.add_node(commit.hexsha, committed=commit.committed_datetime)
            graph.add_edge(
                parent.hexsha,
                commit.hexsha,
            )
    df = DataFrame(columns=['start', 'end'])
    for chain in nx.connected_components(graph):
        nodelist = [graph.nodes[key] for key in chain]
        ordered = sorted(nodelist, key=lambda x: x['committed'])
        row = ordered[0]['committed'], ordered[-1]['committed']
        df.add_row(row)

    return px.line(data_frame=df, x='start', y='end', title='Code Lines')


layout = html.Div(
    [
        html.H2("Lines of Code"),
        html.Button(id="code-lines-refresh-button", children="Refresh"),
        dcc.Graph(id="code-lines-graph")
    ]
)
