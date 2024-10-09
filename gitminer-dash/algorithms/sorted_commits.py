import git


def get_most_recent_tags(repo: git.Repo, desired):
    sorted_tags = sorted(
        repo.tags,
        key=(lambda x: x.commit.authored_datetime)
    )
    last_20 = sorted_tags[-desired:]
    return last_20
