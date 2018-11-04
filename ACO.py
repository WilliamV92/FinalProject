import random as rand
import math as math

class Map:
    def __init__(self, city_count):
        self.city_count = city_count
        self.cities = self.generate_cities()

    
    def generate_cities(self):
        cities = {}
        existing_cities = set()
        while len(existing_cities) != self.city_count:
            x = rand.randint(0, 100)
            y = rand.randint(0, 100)
            existing_cities.add((x, y))
        for i in range(len(existing_cities)):
            cities[i] = City(existing_cities.pop(), i)
        return cities

    def display_cities(self):
        for city in self.cities:
            print(self.cities[city])

class City:
    def __init__(self, coords, id):
        self.x = coords[0]
        self.y = coords[1]
        self.id = id
    def distance_from(self, city):
        return math.hypot(city.x - self.x, city.y -self.y)
    def __str__(self):
        return("ID: {0} X: {1} Y: {2}".format(self.id, self.x, self.y))


new_map = Map(10)
new_map.display_cities()

# def ANTS_SOLVE: 
#   for i in range(0, num_iterations):
#       for k in range(0, num_ants):
#           ant.solve_problem()
#       update_pheromenes()