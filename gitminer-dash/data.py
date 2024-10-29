import os
import re
from functools import cache

from git import Repo

# Link this to any local repo, until we can make this
# a handy-dandy drag-n-drop or dir selection input field
repository_path = "../../ClassDojo/dojo-behavior-ios"


@cache
def get_repo(path: str = repository_path) -> Repo:
    return Repo(path)


def get_repo_name():
    return re.sub(pattern=r'[_\.-]', repl=' ', string=os.path.split(repository_path)[-1]).title()
