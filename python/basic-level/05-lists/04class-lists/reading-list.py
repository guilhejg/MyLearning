import sys
from sys import excepthook

booklist = ['harry potter', '1984', 'the fault in our stars', 'the mom test', 'life in code']
start = print("\nWhat you gonna do?\n1) Insert a New Book\n2) Remove a Book")
home = int(input("\nType Here: "))
if home == 1:
    ans = input("\nWhat Book you want to add?\nAns: ")
    booklist.append(ans)
    print("Sucessfuly added, good day.")
    sys.exit()
elif home == 2:
    ans1 = input("\nWhat Book you want to remove?\nAns: ")
    print(booklist)
    booklist.remove(ans1)
    ans2 = int(input("\nAnother Book you want to remove?\nAns: "))
    print(booklist)
    booklist.pop(ans2)
    print("Sucessfuly removed, good day.")
    print(booklist)
    sys.exit()
