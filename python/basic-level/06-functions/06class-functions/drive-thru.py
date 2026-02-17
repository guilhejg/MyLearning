def welcome():
    print("Welcome to João's Drive Thru!")
    print("Please choose an item:")
    print("1 - 🍔 Cheeseburger")
    print("2 - 🍟 Fries")
    print("3 - 🥤 Soda")
    print("4 - 🍦 Ice Cream")
    print("5 - 🍪 Cookie")
def get_item(choice):

    if choice == 1:
        return "cheessburguer"
    elif choice == 2:
        return "Fries"
    elif choice == 3:
        return "Soda"
    elif choice == 4:
        return "Ice Cream"
    elif choice == 5:
        return "Milk"
    else:
        print("Invald choice")

welcome()
choice = int(input("Please choose an item: "))
print(get_item(choice))