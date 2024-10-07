from functools import cache

from git import Repo

# Link this to any local repo, until we can make this
# a handy-dandy drag-n-drop or dir selection input field
repository_path = "sample_repo"


@cache
def get_repo(path: str) -> Repo:
    return Repo(path)
