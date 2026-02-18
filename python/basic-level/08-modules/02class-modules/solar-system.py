from math import pi
from random import choice as ch

planets = [
  'Mercury',
  'Venus',
  'Earth',
  'Mars',
  'Saturn'
]

r = 0

random_planet = ch(planets)
if random_planet == "Mercury":
    r = 2440
elif random_planet == "Venus":
    r = 6052
elif random_planet == "Earth":
    r = 6371
elif random_planet == "Mars":
    r = 3390
elif random_planet == "Saturn":
    r = 58232
else:
    print("Oops! An error occurred.")

area = 4*pi*r**2
area_rounded = round(area, 2)
print("The Planet is " + random_planet + " and has  " + str(area_rounded) + " square kilometers.")
