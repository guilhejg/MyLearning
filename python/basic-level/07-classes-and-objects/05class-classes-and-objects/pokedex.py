class Pokemon:
    def __init__(self, entry, name, type, description, is_caught):
        self.entry = entry
        self.name = name
        self.type = type
        self.description = description
        self.is_caught = is_caught

    def speak(self):
        print(self.name + " says: " + self.name)

    def display_details(self):
        print("Entry Number: " + str(self.entry))
        print("Name: " + self.name)
        print("Type: " + str(self.type))
        print("Description: " + self.description)
        if self.is_caught:
            print(self.name + " has already been caught!")
        else:
            print(self.name + " has not been caught!")


pikachu = Pokemon(25, "Pikachu", "Electric", "Pikachu has a Pokémon", True)
charmander = Pokemon(4, "Charmander", "Fire", "Charmander is a fire-type Pokémon", True)
bulbasaur = Pokemon(1, "Bulbasaur", "Grass/Poison", "Bulbasaur is a grass-type Pokémon", False)
squirtle = Pokemon(7, "Squirtle", "Water", "Squirtle is a water-type Pokémon", False)
eevee = Pokemon(133, "Eevee", "Normal", "Eevee can evolve into many different forms", True)
jigglypuff = Pokemon(39, "Jigglypuff", "Fairy", "Jigglypuff loves to sing", False)

pikachu.display_details()
print()
charmander.display_details()
print()
bulbasaur.display_details()
print()
squirtle.display_details()
print()
eevee.display_details()
print()
jigglypuff.display_details()
