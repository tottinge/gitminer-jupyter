import logging
import os
from typing import Optional

import git
from dash import Dash, html, dcc, Output, Input
from dash.exceptions import PreventUpdate

repo: Optional[git.Repo] = None
logger = logging.getLogger(__name__)


class IDs:
    REPO_SELECT_BTN: str = "repo-select-btn"
    REPO_UPLOAD_CTRL = "repo-select-ctrl"
    REPO_TEXT_INPUT: str = "repo-text-input"
    LOADING_VIZ: str = "repo-loading-viz"
    LOADED_INDICATOR: str = "repo-loaded-indicator"


app = Dash()

app.layout = html.Div(
    children=[
        html.Div(children=f"Starting at {os.getcwd()}"),
        html.Div(children=[
            html.Label("Repository to evaluate", htmlFor=IDs.REPO_TEXT_INPUT),
            dcc.Input(id=IDs.REPO_TEXT_INPUT, type="text", value="../ClassDojo/dojo-behavior-ios",
                      placeholder="repository path here"),
            html.P(id=IDs.LOADED_INDICATOR, children=["Not Loaded"]),
            dcc.Loading(id=IDs.LOADING_VIZ, children=[html.P("not loaded yet")])
        ])
    ])

def render_selection():
    @app.callback(
        Output(IDs.LOADED_INDICATOR, "children"),
        Input(IDs.REPO_TEXT_INPUT, "value")
    )
    def start_loading(path):
        if not path:
            raise PreventUpdate()
        if os.path.isdir(path):
            return [path]
        return ["oops", f"Maybe {path} is not a directory?"]

    return html.Div(children=[
            html.Label("Repository to evaluate", htmlFor=IDs.REPO_TEXT_INPUT),
            dcc.Input(id=IDs.REPO_TEXT_INPUT,
                      type="text",
                      value="../../ClassDojo/dojo-behavior-ios",
                      placeholder="repository path here"),
            html.P(id=IDs.LOADED_INDICATOR, children=["Not Loaded"]),
    ])





if __name__ == '__main__':
    app.run(debug=True)
