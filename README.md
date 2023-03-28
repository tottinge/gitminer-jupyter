# Git Miner

Exploration of git history via networkx

Initially, the idea is to find "affinity" between files by building a graph where every commit that includes file A and B creates a connection. Which files tend to be committed together? Which never are? What is the structure we should expect?

Future directions: 
* Module structure recommendations
* File recommender ("6 of 12 programmers also edited BLAH.java")
* ???


# Setup

## Create a venv

In shell:

	python -m venv venv
	source venv/bin/activate

## Install the requirements

in shell:

	pip install -r requirements.txt



## Create a Jupyter Kernel
in shell:

	python -m ipykernel install --user --name=gitminer
	
## Launch jupyter

in shell:

    ./run
  
or type:

    jupyter-lab