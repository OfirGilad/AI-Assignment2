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

Let us mark the following parameters: 
1. `Di` - the number of packages agent `i` picked and delivered on time (when termination conditions are met).
2. `Pi` - the number of packages agent `i` picked and not yet delivered (when termination conditions are met).
3. `A` - the number of packages that are still available (when termination conditions are met).
Where the termination conditions are: **goal** or **cutoff** states.

When **goal** conditions are met (at a terminal node), 
we return the following scores depending on the game type:
1. **Adversarial:** `h(n) = (Di - Dj)` (Where agent `j` is the adversary)
2. **A semi-cooperative game:** `h(n) = Di`
3. **A fully cooperative game:** `h(n) = (Di + Dj)` (Where agent `j` is the partner)

But, when **cutoff** conditions are met (at a terminal node), 
we calculate the following static heuristic evaluation function depending on the game type:
1. **Adversarial:** `h(n) = (Di - Dj) + 0.5 * (Pi - Pj)` (Where agent `j` is the adversary)
2. **A semi-cooperative game:** `h(n) = Di + 0.5 * Pi`
3. **A fully cooperative game:** `h(n) = (Di + Dj) + 0.5 * (Pi + Pj) + 0.25 * A` (Where agent `j` is the partner) 

## The rationale behind selecting this Heuristic function:

The rationale for every game type is:
1. `Adversarial:`\
   Each agent aims to maximize its own individual score minus the opposing agent's score.\
   From agent `i`'s perspective, maximizing the following scores:  
   1. `(Di-Dj)` - Its own individual score minus its adversary score.
   2. `(Pi-Pj)` - Its own number of picked packages minus its adversary number of picked packages 
      (where possibly half of those packages might be delivered later in the game).
   
   can increase the changes of agent `i` to achieve the best possible score versus its adversary agent `j`.
2. `A semi-cooperative game:`\
   Each agent tries to maximize its own individual score which is the number of packages it has delivered on time 
   (Or break ties cooperatively).
   So, similar to the adversarial game, maximizing the following scores:  
   1. `Di` - Its own individual score.
   2. `Pi` - Its own number of picked packages 
      (where possibly half of those packages might be delivered later in the game).
   
   can increase the changes of agent `i` to achieve the best possible score.
3. `A fully cooperative game:`\
   Both agents aim to maximize the sum of individual scores.\
   So, maximizing the following scores:  
   1. `(Di+Dj)` - The sum of both agents' individual scores.
   2. `(Pi+Pj)` - The sum of both agents' number of picked packages 
      (where possibly half of those packages might be delivered later in the game).
   3. `A` - The number of packages that are still available.
      (where possibly quarter of those packages might be delivered later in the game).

   can increase the changes of both agents to achieve the best possible sum of individual scores.
