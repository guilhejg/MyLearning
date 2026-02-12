# Checkpoint Project ⛳️

Congratulations on completing the first four chapters of The Legend of Python! Now let's use the skills you've learned (variables, control flow statements, and loops) to build a Python project on your own.

Use the Python Code Editor, Visual Studio Code, or your code editor of choice for this project.

Terminal and our three characters
# Rock Paper Scissors

Rock, Paper, Scissors is a classic game that resonates with folks from around the world.

Create a rock_paper_scissors.py program where the user plays a round of Rock, Paper, Scissors against the computer.
``````
The rules are as follows:

Rock beats Scissors.
Scissors beat Paper.
Paper beats Rock.
First, create a player and a computer variable.

Prompt the player to select number between 1 and 3 with input() and store it in player:

1 is for '✊' (Rock).
2 is for '✋' (Paper).
3 is for '✌️' (Scissors).
Then, use the random.randint() method to assign a number to the computer variable (1 to 3).


Lastly, use control flow to compare the user's choice and the computer's choice, determine the winner, and print out who won.

The output should look something like this:

===================
Rock Paper Scissors
===================

1) ✊
2) ✋
3) ✌️
Pick a number: 2

You chose: ✋
CPU chose: ✊
The player won!