from typing import Protocol, Dict

import pandas as pd


class GitHistoryDataframe(Protocol):
    hash: pd.Series  # of string
    author: pd.Series  # of string
    coauthors: pd.Series  # of lists of strings
    date: pd.Series  # of datetime
    message: pd.Series  # of string
    files: pd.Series  # of dictionaries
    totals: pd.Series  # of dictionaries

    def query(self, query: str) -> pd.DataFrame:
        ...


ChangeSummary = Dict[str, int]
FilesEntry = Dict[str, ChangeSummary]
