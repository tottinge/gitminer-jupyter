import typer
from git import Repo
from typing_extensions import Annotated

app = typer.Typer()


@app.command("most_committed")
def cli_most_committed(
        json_file: str,
        max_to_list: Annotated[int, typer.Option("--size", "-s")] = 5
):
    """
    List the files that have been committed the most often
    """
    from most_commited import count_files_in_commits
    count_files_in_commits(json_file, max_to_list)


@app.command("extract_to_json")
def cli_extract_to_json(repo_path: str):
    """
    Extract the contents of a git repo to a json file
    """
    from extractor import dump_it
    source: Repo = Repo(repo_path)
    dump_it(source)


if __name__ == "__main__":
    app()
