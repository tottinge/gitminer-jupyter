from dash import html, register_page, dcc, callback, Output, Input
from dash.dash_table import DataTable
import plotly.express as px
from pandas import DataFrame

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

@callback(
    Output('page-content', 'figure'),
    Input('period-dropdown', 'value')
)
def populate_graph(period_input):
    frame = DataFrame(data=fake_data, columns=['filename', 'count'])
    return px.bar(data_frame=frame, x='filename', y='count')

@callback(
    Output('table-data', 'data'),
    Input('period-dropdown', 'value')
)
def populate_table(period_input):
    frame = DataFrame(data=fake_data, columns=['filename', 'count'])
    return frame.to_dict('records')
