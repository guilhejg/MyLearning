# day in life
import sys
print("===========================================\nHello, welcome to the DAY IN LIFE minigame!\n===========================================")
ans1 = int(input("Select a name\n1) Mattheo\n2) Theo\n3) Catarina\n4) Exit\nType Here: "))
score = 0
name = ""
if ans1 == "1":
    name = "Mattheo"
    score += 1
if ans1 == "2":
    name = "Theo"
    score += 1
if ans1 == "3":
    name = "Catarina"
    score += 1
if ans1 == "4":
    sys.exit(0)
print("\nCongratulations! You've selected your name!\nLet's go " + name)
print("\n")
#===== Code Division
ans2 = int(input("Select Your Car to go to the work!\n1) Ford Mustang\n2) Chevrolet Camaro\n3) BYD Dolphin MIni\n4) Chevrolet Chevette\nType Here: "))
if ans2 == "1":
    score += 2
if ans2 == "2":
    score += 2
if ans2 == "3":
    score += 1
if ans2 == "4":
    score += 4
print("You've selected your Car to go to the work!")

ans3 = print("Select Your Work!\n1) Medic\n2) Police\n3) Pilot\n4) Cientist\nType Here: ")
if ans3 == "1":
    score += 3
if ans3 == "2":
    score += 3
if ans3 == "3":
    score += 10
if ans3 == "4":
    score += 4
print("You've selected your Work!")
print("\n")
result = print("Great Work! Your Finish Day Score is" + str(score))


