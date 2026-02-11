Slytherin = 0
Hufflepuff = 0
Ravenclaw = 0
Gryffindor = 0

Q1 = int(input("Q1) Do you like Dawn or Dusk?\n1) Dawn\n2) Dusk\nType Your Answer Here: "))
print("\n")

if Q1 == 1:
    Gryffindor += 1
    Ravenclaw += 1
elif Q1 == 2:
    Hufflepuff += 1
    Slytherin += 1
else: print("Wrong input")

Q2 = int(input("\nQ2) When I’m dead, I want people to remember me as:\n1) The Good\n2) The Great\n3) The Wise\n4) The Bold\nTyper Your Answer Here: "))
print("\n")

if Q2 == 1:
    Hufflepuff += 2
elif Q2 == 2:
    Slytherin += 2
elif Q2 == 3:
    Ravenclaw += 2
elif Q2 == 4:
    Gryffindor += 2
else: print("Wrong input")

Q3 = int(input("Q3) Which kind of instrument most pleases your ear?\n1) The violin\n2) The trumpet\n3) The piano\n4) The drum\nType Your Answer Here: "))
print("\n")

if Q3 == 1:
    Slytherin += 4
elif Q3 == 2:
    Hufflepuff += 4
elif Q3 == 3:
    Ravenclaw += 4
elif Q3 == 4:
    Gryffindor += 4
else: print("Wrong input")

maior = max(Gryffindor, Ravenclaw, Hufflepuff, Slytherin)
if maior == Gryffindor:
    print("🏆 You belong to Gryffindor!")
elif maior == Ravenclaw:
    print("🏆 You belong to Ravenclaw!")
elif maior == Hufflepuff:
    print("🏆 You belong to Hufflepuff!")
elif maior == Slytherin:
    print("🏆 You belong to Slytherin!")

print("Gryffindor: ", Gryffindor)
print("Ravenclaw: ", Ravenclaw)
print("Hufflepuff: ", Hufflepuff)
print("Slytherin: ", Slytherin)





