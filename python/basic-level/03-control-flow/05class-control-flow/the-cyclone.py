height = 137
credits = 10

Hperson = int(input("Whats your Height? "))
Cperson = int(input("How many credits you have? "))

if Hperson >= height and Cperson >= credits:
  print("Enjoy the ride!")
elif Hperson >= height and Cperson < credits:
    print("You Don't Have enought Credits ")
elif Hperson < height and Cperson >= credits:
  print("You Doens't have the enought heigh to enjoy the ride! ")
elif Hperson < height and Cperson < credits:
  print("You Just Can't enjoy this ride, you don't entry on any requirements, saddently. ")