from typing import cast

import pandas

from gminer.types import GitHistoryDataframe


def read_git_history_from_file(json_file: str) -> GitHistoryDataframe:
    return cast(GitHistoryDataframe, pandas.read_json(json_file))
