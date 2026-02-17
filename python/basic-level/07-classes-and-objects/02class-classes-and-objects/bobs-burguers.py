class Restaurant:
    def __init__(self):
        self.name = ""
        self.category = ""
        self.rating = 0.0
        self.delivery = False

bobsburguers = Restaurant()
bobsburguers.name = "Bob's Burguers"
bobsburguers.category = "Fast Food"
bobsburguers.rating = 4.7
bobsburguers.delivery = True

print(vars(bobsburguers))