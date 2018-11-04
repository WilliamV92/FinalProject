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


class Ant:
    def __init__(self, problem):
        self.problem = problem
        self.visited_cities = []
        self.tour_length = 0

    def visit_city(self, city_id):
        self.visited_cities.append(city_id)
    
    def has_visited(self, city_id):
        return not city_id not in self.visited_cities

    def update_tour_length(self, current_city_id, city_id):
        distance = 0
        # calculate distane from current_city_id to city_id
        return self.tour_length + distance
    
    def tour_map(self, start_city_id):
        # we need something that if its the first iteration, we make them all start off in random directions
        # because we have no pheromone values yet...so we don't want them all just doing them same thing
        # by basically doing a shortest path algorithm...
        num_cities = len(map)
        current_city_id = start_city_id
        for i in range(0, num_cities):
            # determine probability to travel to each city from current city
            visit_probailities = self.calculate_probailities(current_city_id)
            # choose next city to visit
            next_city_id = self.choose_next_city(visit_probailities)
            # visit city and update trail length
            self.visit_city(next_city_id)
            self.update_tour_length(current_city_id, next_city_id)
            current_city_id = next_city_id
        # when I have visited final city, go back to start, and update tour length?
    
    def calculate_probailities(self, current_city_id):
        # at index 0 is the probability for visiting city with id 0
        visit_probabilities = []
        # calculate sum of (T(i-j) * alpha) * (N(i-j) * beta) for all cities ant has not yet visited
        #       loop through all cities, check if visited, if not, add to sigma value
        # calculate probailities for all cities any has not visited yet:
        # pheromone_trails (T(i-j) * alpha) * (N(i-j) * beta) / sigma
        #       loop throug all cities, if visited probaility = 0, else calculate probaility
        return visit_probabilities
    
    def choose_next_city(self, visit_probabilities):
        # make choice of which city to visit based on probailities
        city_id = 0
        return city_id


# ant:
    # adds to know: (1) the map; (2) matrix of pheromenes (pheromone_trails[][])
    # list of visited cities: A, D, E, F
    # function to mark city as visited
    #    def visit_city(city_id):
    #        visited_cities.add(city_id)
    # calculate tour length (based on visitied cities and map)
    # do_tour() generate_solution()
    #   pick next city()
    #       calculate probabilities()


class AntColony:
    def __init__(self, problem):
        self.problem = problem
        self.ants = []
        self.best_tour = None
        self.initialize_colony()
    
    def initialize_colony(self):
        # make all ants and add them to list...number of limits based on problem (i.e, num of cities?)
        # initialize the ants?
        self.ants.append(Ant(self.problem))

    def solve_problem(self):
        # psuedocode for AC0
        # for i in range(0, num_iterations):
        #       for k in range(0, num_ants):
        #           ant.solve_problem()
        #       update_pheromenes()
        return self.best_tour

# colony:
    # list of ants
    # best tour found
    # update pheromenes():
        # updates pheromone values on each edge

    # solve_problem:
        # def ANTS_SOLVE: 
        #   for i in range(0, num_iterations):
        #       for k in range(0, num_ants):
        #           ant.solve_problem()
        #       update_pheromenes()

class Problem:
    def __init__(self, num_cities):
        self.map = Map(num_cities)
        self.distance_matrix = []
        self.pheromone_trails = []
        self.initialize(num_cities)
    
    def initialize(self, num_cities):
        # pre-calculate distances between all cities in maps
        self.distance_matrix = [] 
        for i in range(len(self.map.cities.keys())):
            temp_distances = []
            for j in range(0, len(self.map.cities.keys())):
                if i == j:
                    temp_distances.append(0)
                elif j < i:
                    temp_distances.append(self.distance_matrix[j][i])
                else:
                    city1 = self.map.cities[i]
                    city2 = self.map.cities[j]
                    distance = math.hypot((city1.x - city2.x), (city1.y - city2.y))
                    temp_distances.append(distance)
            self.distance_matrix.append(temp_distances)
        # prepopulate pheromone matrix with value of 1 for each edge
        self.pheromone_trails = []
        for i in range(num_cities):
            temp_trail = []
            for j in range(num_cities):
                temp_trail.append(1)
            self.pheromone_trails.append(temp_trail)

def main():
    # generate problem with 10 cities
    problem = Problem(10)
    # create colony and give it the problem
    colony = AntColony(problem)
    # solve problem with colony
    colony.solve_problem()

problem = Problem(10)
for x in range(len(problem.distance_matrix)):
    for y in range(len(problem.distance_matrix)):
        print(problem.distance_matrix[x][y], end=",", flush=True)
    print()