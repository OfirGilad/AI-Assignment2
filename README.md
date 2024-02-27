# Introduction to Artificial Intelligence - Programming Assignment 2

## Detailed installation instructions:

In order to run the code create a Python environment as follows: \
`Python3.10` \
`numpy==1.26.3`

And to run the project:
1. open the [main.py](src/main.py) script.
2. Update the `data_filepath` parameter with the path to the input txt file.
3. Run the `main` function.

To change the game type mode:
1. Select the input `.txt` file from the `input` folder.
2. Change the `#G` parameter in the `.txt` file to one of the following options:
    - 1 - `Adversarial (zero sum game)`
    - 2 - `A semi-cooperative game`
    - 3 - `A fully cooperative game`

## About the Heuristic function we used:

Let Pi be the number of packages agent i picked and delivered on time when termination conditions are met (at a terminal node).
The heuristic evaluation function is based on the number of delivered packages and depends on the game type: 
1. `Adversarial:` _h(n) = Pi - Pj_ (Where agent _j_ is the adversary)
2. `A semi-cooperative game:` _h(n) = Pi_
3. `A fully cooperative game:` _h(n) = Pi + Pj_ (Where agent _j_ is the partner) 

## The rationale behind selecting this Heuristic function:

The rationale for every game type is:
1. `Adversarial:`\
Each agent aims to maximize its own individual score minus the opposing agent's score.\
From agent i's perspective, Pi is its own individual score while Pj is the opposing agent's score, making Pi-Pj fit for this description.
2. `A semi-cooperative game:`\
Each agent tries to maximize its own individual score which is the number of packages it has delivered on time - Pi.
3. `A fully cooperative game:`\
Both agents aim to maximize the sum of individual scores (their Pi values).\
The heuristic function fits this game type as it counts how many packages were delivered on time.
In other words, it sums up all individual scores.
