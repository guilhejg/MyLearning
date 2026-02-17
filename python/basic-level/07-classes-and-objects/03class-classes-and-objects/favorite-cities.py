class City:
    def __init__(self):
        self.name = ""
        self.country = ""
        self.population = 0
        self.landmarks = []
        self.culture = ""
        self.food = ""

cuiaba = City()
cuiaba.name = "Cuiabá"
cuiaba.country = "Mato Grosso"
cuiaba.population = 860000
cuiaba.landmarks = ["Catedral Bom Despacho"]
cuiaba.culture = "Acolhedora"
cuiaba.food = "Maria Isabel"

england = City()
england.name = "England"
england.country = "England"
england.population = 800000
england.landmarks = ["Time Tower"]
england.culture = "Kingdon"
england.food = "Tea"

print(vars(cuiaba))
print(vars(england))