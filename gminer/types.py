from enum import StrEnum
from typing import Protocol, Dict, Iterable

import pandas as pd


class GitHistoryDataframe(Protocol):
    columns: Iterable[str]
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


class FEKey(StrEnum):
    filename = "filename"
