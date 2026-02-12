import math
import sys
print("==================\nArea Calculator 📐\nby João Guilherme\n==================\n1) Triangle\n2) Rectangle\n3) Square\n4) Circle\n5) Quit\n\n")
ans = int(input("Which Shape:   "))
if ans == 5:
    sys.exit()
elif ans == 4:
    raio = int(input("Raio:   "))
    area = math.pi * raio**2
else:
    base = int(input("Base:   "))
    height = int(input("Height:   "))
    if ans == 1:
        area = (base * height) / 2
    if ans == 2:
        area = (base * height)
    if ans == 3:
        area = (base)*4
print(area)
