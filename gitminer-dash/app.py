
from dash import html, dcc, Dash, page_container, page_registry

app = Dash(__name__, use_pages=True)

app.layout = html.Div([
    html.H1("The Git Miner: Interactive", style={"text-align": "center"}),
    html.Div([
        dcc.Link(page['name'], href=page['path'])
        for page in page_registry.values()
    ], style={
        "display": "flex",
        "justify-content": "space-between"
    }),
    page_container
])

if __name__ == '__main__':
    app.run_server(debug=True)
