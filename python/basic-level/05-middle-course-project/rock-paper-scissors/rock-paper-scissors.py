import random

print("=========================\n👾 Rock Paper Scissors 👾\n=========================\n1) Rock ✊\n2) Paper 🖐️\n3) Scissors ✌️\n4) Quit\n\n")
ans = int(input("What do you choose? "))
res = random.randint(1,3)
type = res
if ans == 1 and res == 1:
    print("Draw!")
if ans == 1 and res == 2:
    print("You lose!")
if ans == 1 and res == 3:
    print("You win!")
#====
if ans == 2 and res == 1:
    print("You win!")
if  ans == 2 and res == 2:
    print("Draw!")
if ans == 2 and res == 3:
    print("You lose!")
#===
if ans == 3 and res == 1:
    print("You lose!")
if ans == 3 and res == 2:
    print("You Win!")
if ans == 3 and res == 3:
    print("Draw")
#===
if type == 1:
    print("The Other Choice is ROCK!")
if type == 2:
    print("The Other Choice is PAPER!")
if type == 3:
    print("The Other Choice is SCISSORS!")
