# dry.py

name = input("What's your name? ")
# input(): pauses the program and waits for the user to type something.
# The value entered is returned as a string.

age_str = input("How old are you? ")
# input(): reads user input again. All input values are strings by default.

age = int(age_str)
# int(): converts a value into an integer number.
# Here it converts the age from string to integer.

print("Hello,", name)
# print(): displays information on the screen.

# New built-in function: divmod()
# divmod(a, b) returns a tuple containing:
# (integer division result, remainder of the division).
quotient, remainder = divmod(age, 5)

print(f"Dividing your age by 5 gives quotient={quotient} and remainder={remainder}.")
# print(): displays formatted text using an f-string.

# this code has writed by chatGPT.