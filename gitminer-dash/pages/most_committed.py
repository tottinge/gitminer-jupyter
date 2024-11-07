from collections import Counter
from datetime import datetime, timedelta

import plotly.express as px
from dash import html, register_page, dcc, callback, Output, Input
from dash.dash_table import DataTable
from dash.exceptions import PreventUpdate
from pandas import DataFrame

import data

fake_data = [
    ("common.py", 800),
    ("rare.py", 45)
]

register_page(
    module=__name__,  # Where it's found
    name="Most Committed",  # Menu item name
)

layout = html.Div(
    [
        html.H2("Most Often Committed Files"),
        dcc.Dropdown(id='period-dropdown', options=[
            'Last 30 days',
            'Last 60 days',
            'Last 90 days'
        ], value='Last 30 days'),
        # html.Div(id='page-content', children=[]),
        dcc.Graph(id='page-content', figure={"data": []}),
        html.Hr(),
        html.H2("Source Data"),
        html.Div(
            id='id-most-committed-graph-holder',
            style={"display": "none"},
            children=[
                DataTable(id='table-data')
            ]
        ),
    ]

)


def calculate_usages(period: str):
    period = period or ""
    days = 14
    if "30" in period:
        days = 30
    elif "60" in period:
        days = 60
    elif "90" in period:
        days = 90

    end = datetime.today().astimezone()
    begin = end - timedelta(days=days)

    counter = Counter()
    all_commits = list(data.commits_in_period(begin, end))
    for commit in all_commits:
        try:
            files = commit.stats.files.keys()
            counter.update(files)
        except ValueError as e:
            print("Stop me if you've seen this one before")
            raise e
    return counter.most_common(25)


@callback(
    [
        Output('page-content', 'figure'),
        Output('table-data', 'data'),
        Output('id-most-committed-graph-holder', 'style')
    ],
    Input('period-dropdown', 'value')
)
def populate_graph(period_input):
    if not period_input:
        raise PreventUpdate
    usages = calculate_usages(period_input)
    frame = DataFrame(data=usages, columns=['filename', 'count'])
    figure = px.bar(data_frame=frame, x='filename', y='count')

    frame = DataFrame(data=usages, columns=['filename', 'count'])
    table_data = frame.to_dict('records')

    style_show = {"display": "block"}
    return figure, table_data, style_show
