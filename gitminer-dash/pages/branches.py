import dash
from dash import html

dash.register_page(__name__)

layout = html.Div(
    [
        html.H2("This is the branches page"),
    ]
)
