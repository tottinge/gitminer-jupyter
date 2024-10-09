import dash
from dash import html

dash.register_page(__name__, title="Merge Sizes")

layout = html.Div(
    [
        html.H2("This is the merges page"),
    ]
)
