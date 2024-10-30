from dash import html, register_page, dcc
from dash.dash_table import DataTable

register_page(
    module=__name__,  # Where it's found
    name="Most Committed",  # Menu item name
)

layout = html.Div(
    [
        html.H2("Most Often Committed Files"),
        dcc.Dropdown(id='period-dropdown', options=['Last 30 days', 'Last 60 days']),
        html.Div(id='page-content', children=[]),
        html.Hr(),
        html.H2("Source Data"),
        DataTable()
    ]
)
