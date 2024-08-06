import json
import logging
import os
from typing import Optional

import git
import plotly.express as px
from dash import Dash, html, dcc, Output, Input, State
from dash.exceptions import PreventUpdate

from gminer.miner import release_tag_intervals

repo: Optional[git.Repo] = None
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Dash()


class IDs:
    REGEX_TEXT_INPUT = "release_tag_regex_input"
    GLOBAL_STATE_JSON = "global-state-json"
    REPO_SELECT_BTN: str = "repo-select-btn"
    REPO_UPLOAD_CTRL = "repo-select-ctrl"
    REPO_TEXT_INPUT: str = "repo-text-input"
    LOADED_INDICATOR: str = "repo-loaded-indicator"
    GRAPH_RELEASE_FREQUENCY: str = "repo-release-frequency"


def render_selection():
    @app.callback(
        Output(IDs.GLOBAL_STATE_JSON, "data"),
        Input(IDs.REPO_SELECT_BTN, "n_clicks"),
        State(IDs.REPO_TEXT_INPUT, "value"),
        prevent_initial_call=True
    )
    def start_loading(_, repo_path):
        data = {}
        if not os.path.isdir(repo_path):
            data["error_msg"] = f'"{repo_path}" is not a directory'
        else:
            try:
                global repo
                git.Repo(repo_path)
                data["repo_path"] = repo_path
            except git.GitError as err:
                data["error_msg"] = f"{err} is not a git repository."
        return json.dumps(data)

    @app.callback(
        Output(IDs.LOADED_INDICATOR, "children"),
        Input(IDs.GLOBAL_STATE_JSON, "data")
    )
    def display_loaded_indicator(data_string):
        data = json.loads(data_string) if data_string else {}
        logging.warning(f"Loaded indicator call for: {data}")
        if not data:
            return ["No repository loaded"]
        error_msg = data.get("error_msg")
        if error_msg:
            return [f"No Repo Loaded. {error_msg}"]
        return html.Div(children=[f"Loading {data.get('repo_path')}"])

    @app.callback(
        Output(IDs.GRAPH_RELEASE_FREQUENCY, "figure"),
        Input(IDs.GLOBAL_STATE_JSON, "data")
    )
    def display_graph_release_frequency(data_string):
        graph_points = 24
        data = json.loads(data_string) if data_string else {}
        if not data:
            raise PreventUpdate()

        repo_path = data.get('repo_path')
        if not repo_path:
            raise PreventUpdate()

        git_repo = git.Repo(repo_path)
        full_tag_df = release_tag_intervals(git_repo, 'production')

        # Drop all but the last 35 - you need at least one more than you graph
        sizing_df = full_tag_df.tail(graph_points + 1).copy()

        # Calc Sizes
        current_labels = sizing_df['name'].tolist()  # 1 2 3 4
        previous_labels = [None] + current_labels[:-1]  # none, 1, 2, 3
        diffs = []
        for current, previous in zip(current_labels, previous_labels):
            changes = (git_repo.commit(current).diff(previous)) if previous else []
            diffs.append(len(changes))
        sizing_df["change_size"] = diffs

        # Truncate to last 30
        final_df = sizing_df.tail(graph_points)

        # Draw
        figure = px.bar(final_df,
                        x="timestamp",
                        y="change_size",
                        title=f"Last {len(final_df)} Releases",
                        hover_data=["name", "timestamp", "change_size"],
                        labels={
                            'timestamp': 'Date of Release',
                            'change_size': 'Changes (diff counts)',
                            'name': 'Label'
                        },
                        color='change_size',
                        color_continuous_scale=px.colors.get_colorscale('turbo')
                        )

        # figure.update_traces(width=10)
        return figure

    return html.Div(children=[
        html.Div(children=[
            html.Label("Regex for release tags", htmlFor=IDs.REGEX_TEXT_INPUT),
            dcc.Input(id=IDs.REGEX_TEXT_INPUT, type="search", size="128"),
        ]),
        html.Div(children=[
            html.Label("Repository to evaluate", htmlFor=IDs.REPO_TEXT_INPUT),
            dcc.Input(id=IDs.REPO_TEXT_INPUT,
                      type="text",
                      value="",
                      size="128",
                      placeholder="repository path here",
                      autoComplete="True"),
        ]),
        html.Button("Load", type="Submit", id=IDs.REPO_SELECT_BTN),
        html.P(id=IDs.LOADED_INDICATOR, children=["Not Loaded"]),
        dcc.Graph(id=IDs.GRAPH_RELEASE_FREQUENCY),
    ])


if __name__ == '__main__':
    app.layout = html.Div(
        children=[
            html.Div(children=f"Starting at {os.getcwd()}"),
            html.Br(),
            dcc.Store(id=IDs.GLOBAL_STATE_JSON),
            render_selection()
        ])
    app.run(debug=True)
