import logging
import os
from typing import Optional

import git
from dash import Dash, html, dcc, Output, Input
from dash.exceptions import PreventUpdate

repo: Optional[git.Repo] = None
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Dash()


class IDs:
    REPO_SELECT_BTN: str = "repo-select-btn"
    REPO_UPLOAD_CTRL = "repo-select-ctrl"
    REPO_TEXT_INPUT: str = "repo-text-input"
    LOADING_VIZ: str = "repo-loading-viz"
    LOADED_INDICATOR: str = "repo-loaded-indicator"


last_clicks = 0


def render_selection():
    @app.callback(
        Output(IDs.LOADED_INDICATOR, "children"),
        Input(IDs.REPO_SELECT_BTN, "n_clicks"),
        Input(IDs.REPO_TEXT_INPUT, "value")
    )
    def start_loading(clicks, path):
        global last_clicks
        if last_clicks == clicks:
            raise PreventUpdate()
        last_clicks = clicks
        logger.warning("Loader method called")
        if os.path.isdir(path):
            try:
                global repo
                repo = git.Repo(path)
                return html.Div("Loaded the repo!")
            except Exception as err:
                return html.Div(f"Failed to load: {err}")
        return ["oops", f"Maybe {path} is not a directory?"]

    return html.Div(children=[
        html.Label("Repository to evaluate", htmlFor=IDs.REPO_TEXT_INPUT),
        dcc.Input(id=IDs.REPO_TEXT_INPUT,
                  type="text",
                  value="../../ClassDojo/dojo-behavior-ios",
                  placeholder="repository path here"),
        html.Button("Submit", id=IDs.REPO_SELECT_BTN),
        html.P(id=IDs.LOADED_INDICATOR, children=["Not Loaded"]),
    ])


if __name__ == '__main__':
    app.layout = html.Div(
        children=[
            html.Div(children=f"Starting at {os.getcwd()}"),
            html.Br(),
            render_selection()
        ])
    app.run(debug=True)
