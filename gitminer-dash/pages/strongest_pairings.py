from collections import defaultdict
from datetime import datetime, timedelta
from itertools import combinations

from dash import register_page, html, callback, Output, Input
from dash.dash_table import DataTable
from dash.dcc import Dropdown

import data

periods = {
    "Last 7 Days": 7,
    "Last 30 Days": 30,
    "Last 60 days": 60,
    "Last 90 days": 90
}

register_page(__name__)

layout = html.Div(
    children=[
        html.H1("Strongest Commit Affinities"),
        Dropdown(
            id="id-pairings-period-dropdown",
            options=[x for x in periods.keys()],
            value=[x for x in periods.keys()][0],
        ),
        DataTable(
            id="id-strongest-pairings-table",
            columns=[
                {"name": i, "id": i, 'presentation': 'markdown'}
                for i in ['Affinity', 'Pairing']
            ],
            style_cell={'textAlign': 'left'},
            data=[]
        )
    ]
)


def create_affinity_list(start: datetime, end: datetime) -> list[dict[str, str]]:
    affinities = defaultdict(int)
    for commit in data.commits_in_period(start, end):
        files_in_commit = len(commit.stats.files)
        if files_in_commit < 2:
            continue
        for combo in combinations(commit.stats.files, 2):
            ordered_key = tuple(sorted(combo))
            affinities[ordered_key] += 1 / files_in_commit
    affinity_first_list = [
        dict(Affinity=f"{value:6.2f}", Pairing="\n\n".join(key))
        for key, value in affinities.items()
    ]
    sorted_by_strength = sorted(affinity_first_list, reverse=True, key=lambda x: x['Affinity'])
    return sorted_by_strength[:50]


@callback(
    Output("id-strongest-pairings-table", "data"),
    Input("id-pairings-period-dropdown", "value"),
)
def handle_period_selection(period: str):
    ending = datetime.today().astimezone()
    starting = ending - timedelta(days=periods[period])
    data = create_affinity_list(starting, ending)
    if not data:
        return [{"Affinity": "-----",
                 "Pairing": "No commits detected in period"}]
    return data
