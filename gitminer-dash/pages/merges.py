from datetime import datetime, timedelta

import dash
import pandas as pd
import plotly.express as px
from dash import html, dcc
from dash.dash_table import DataTable

dash.register_page(__name__, title="Merge Sizes")


# Doing this synchronously here (called in the layout)
# makes startup time very slow.
def prepare_dataframe():
    import data
    repo = data.get_repo()

    recent_date = datetime.today().astimezone() - timedelta(days=30)
    recent_merges = [commit for commit in repo.iter_commits()
                     if commit.committed_datetime > recent_date
                     and len(commit.parents) > 1]

    columns = ["hash", "date", "comment", "lines", "files"]
    source = (
        (commit.hexsha,
         commit.committed_datetime.date(),
         commit.message,
         commit.stats.total["lines"],
         commit.stats.total["files"])
        for commit in recent_merges
    )
    result = pd.DataFrame(source, columns=columns).sort_values(by="date")
    print(result)
    return result


layout = html.Div(
    [
        html.H2("Merge Magnitudes"),
        dcc.Source(id='merge-data', ),
        dcc.Graph(
            id="merge-graph",
            figure=px.bar(
                data := prepare_dataframe(),
                x="date",
                y="lines",
                color="files",
                hover_name="date",
                hover_data=["files", "lines", "comment"]
            )),
        html.Hr(),
        html.H2("Raw Data"),
        DataTable(data=data.to_dict("records"))
    ]
)
