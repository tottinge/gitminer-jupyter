# Git Miner

Exploration of maintenance patterns in git.

# How it works

This git miner has two phases. The first is to extract the history from a
git repository (see `git extract-to-json`). This should be directed to a file,
preferably with a .json file extension.

Once you have that extract, you can run the various analytic tools on
the json file. You don't need to have the source code or the actual
git repository handy.

There is a dash app for visualization. You may launch it by going to the gitminer-dash directory and typing 'python
app.py _repo-path_ where
_repo_path_ is the directory path to a repository on your computer.

# Setup

## Create a venv

In shell:

	python -m venv venv
	source venv/bin/activate

Build it:

    python -m build

Install miner:

    pip install path/to/whl/file/blah.whl

To run it:

    miner --help



