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
        dcc.Dropdown(id='period-dropdown', options=['Last 30 days', 'Last 60 days']),
        # html.Div(id='page-content', children=[]),
        dcc.Graph(id='page-content'),
        html.Hr(),
        html.H2("Source Data"),
        DataTable(id='table-data')
    ]

)


def calculate_usages(period: str):
    period = period or ""
    days = 14
    if "30" in period:
        days = 30
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
    Output('page-content', 'figure'),
    Input('period-dropdown', 'value')
)
def populate_graph(period_input):
    if not period_input:
        raise PreventUpdate
    usages = calculate_usages(period_input)
    frame = DataFrame(data=usages, columns=['filename', 'count'])
    return px.bar(data_frame=frame, x='filename', y='count')


@callback(
    Output('table-data', 'data'),
    Input('period-dropdown', 'value'),
    prevent_initial_call=True
)
def populate_table(period_input):
    if not period_input:
        raise PreventUpdate
    usages = calculate_usages(period_input)
    frame = DataFrame(data=usages, columns=['filename', 'count'])
    return frame.to_dict('records')
