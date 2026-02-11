# PH Levels
ph = int(input("What's the pH of the element?"))
if ph == 7:
  print("Neutral")
elif ph > 7:
  print("Basic")
elif ph < 7:
  print("Acidic")