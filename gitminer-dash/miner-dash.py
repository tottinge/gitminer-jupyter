import logging
import os
from typing import Optional

import git
from dash import Dash, html, dcc, Output, Input, State
from git import GitError

repo: Optional[git.Repo] = None
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Dash()


class IDs:
    REPO_SELECT_BTN: str = "repo-select-btn"
    REPO_UPLOAD_CTRL = "repo-select-ctrl"
    REPO_TEXT_INPUT: str = "repo-text-input"
    LOADED_INDICATOR: str = "repo-loaded-indicator"
    GRAPH_RELEASE_FREQUENCY: str = "repo-release-frequency"


def render_selection():
    @app.callback(
        Output(IDs.LOADED_INDICATOR, "children"),
        Input(IDs.REPO_SELECT_BTN, "n_clicks"),
        State(IDs.REPO_TEXT_INPUT, "value"),
        prevent_initial_call=True
    )
    def start_loading(n_clicks, path, global_state):
        logger.warning(f"Clicks: {n_clicks}, path: {path}")
        if os.path.isdir(path):
            try:
                global repo
                repo = git.Repo(path)
                return html.Div("Loaded the repo!")
            except GitError as err:
                return html.Div(f"Failed to load: {err}")
        return ["Oops! ", f"Maybe {path} is not a directory?"]

    return html.Div(children=[
        html.Label("Repository to evaluate", htmlFor=IDs.REPO_TEXT_INPUT),
        dcc.Input(id=IDs.REPO_TEXT_INPUT,
                  type="text",
                  value="../../ClassDojo/dojo-behavior-ios",
                  placeholder="repository path here"),
        html.Button("Load", id=IDs.REPO_SELECT_BTN),
        dcc.Graph(id=IDs.GRAPH_RELEASE_FREQUENCY),
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
