import random as rand
import math as math
import sys
from graphics import *

# ACO Parameters to tune algorithm performance
ALPHA = 0.25 # the importance of pheromene (Tij) in choosing next city
BETA = 5.0 # the importance of cost (Nij) in chosing next city
EVAPORATION_RATE = 0.25 # the rate at which pheromene evaporates from trail
Q = 100 # the total amount of pheromoene left on a trail by an ant
NUMBER_OF_ITERATIONS = 10 # the number of iterations to let ants explore map
BASE_RANDOM_CHOICE_RATE = 0.3 # base rate at which ants will pick a random city (decreases with each iteration)
DISPLAY_WIDTH = 600
DISPLAY_HEIGHT = 800
win = GraphWin(title="ACO", width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)
win2 = GraphWin(title="Nearest Neighbor", width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)

class Map:
    def __init__(self, city_count):
        self.city_count = city_count
        self.cities = self.generate_cities()

    
    def generate_cities(self):
        cities = {}
        existing_cities = set()
        while len(existing_cities) != self.city_count:
            x = rand.randint(50, DISPLAY_WIDTH - 50)
            y = rand.randint(50, DISPLAY_HEIGHT - 50)
            existing_cities.add((x, y))
        for i in range(len(existing_cities)):
            new_city = City(existing_cities.pop(), i)
            cities[i] = new_city
        return cities

    def display_cities(self):
        for city in self.cities:
            print(self.cities[city])

class City():
    def __init__(self, coords, id):
        self.x = coords[0]
        self.y = coords[1]
        self.id = id
    def distance_from(self, city):
        return math.hypot(city.x - self.x, city.y -self.y)
    def __str__(self):
        return("ID: {0} X: {1} Y: {2}".format(self.id, self.x, self.y))


# new_map = Map(10)
# new_map.display_cities()


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
        self.tour_length += self.problem.distance_matrix[current_city_id][city_id]
    
    def tour_map(self, iteration):
        # we need something that if its the first iteration, we make them all start off in random directions
        # because we have no pheromone values yet...so we don't want them all just doing them same thing
        # by basically doing a shortest path algorithm...
        current_city_id = self.problem.start_city_id
        self.visit_city(self.problem.start_city_id)
        for i in range(0, self.problem.num_cities - 1):
            # determine probability to travel to each city from current city
            visit_probailities = self.calculate_probabilities(current_city_id)
            # choose next city to visit
            next_city_id = self.choose_next_city(visit_probailities, iteration)
            # visit city and update trail length
            self.visit_city(next_city_id)
            self.update_tour_length(current_city_id, next_city_id)
            current_city_id = next_city_id
        # when I have visited final city, go back to start, and update tour length?
        self.visit_city(self.problem.start_city_id)
        self.update_tour_length(current_city_id, self.problem.start_city_id)
    
    def calculate_probabilities(self, current_city_id):
        # at index 0 is the probability for visiting city with id 0
        visit_probabilities = []
        edge_scores = []
        pheromone_total = 0.0
        for i in range(self.problem.num_cities):
            if i not in self.visited_cities and i != current_city_id:
                edge_pheromone = math.pow(self.problem.pheromone_trails[current_city_id][i], ALPHA)
                edge_cost = math.pow(1.0 / self.problem.distance_matrix[current_city_id][i], BETA)
                # this calculation is used below as well. saving for later use
                edge_scores.append(edge_pheromone * edge_cost)
                pheromone_total += edge_scores[i]
            else:
                edge_scores.append(0)

        for i in range(self.problem.num_cities):
            if(i in self.visited_cities):
                visit_probabilities.append(0)
            else:
                visit_probabilities.append(edge_scores[i] / pheromone_total)
        return visit_probabilities
    
    # ant's decision logic for choosing next city. The ant will either choice the next
    # city to visit randomly or based on the probabilities matrix returned by calculate_probailities 
    def choose_next_city(self, visit_probabilities, iteration):
        # ant should pick a random city in some cases, especially early on, to make sure we explore
        # the search space. decrease rate of random choice over time
        rand_choice = rand.uniform(0, 1)
        random_choice_rate = BASE_RANDOM_CHOICE_RATE / (iteration + 1)
        if (iteration == 0 and len(self.visited_cities) == 1) or rand_choice < random_choice_rate:
            # also random choice for first move from starting city on the first iteration...
            return self.choose_next_city_random()
        else:
            # make choice of which city to visit based on probailities
            return self.choose_next_city_probabilistic(visit_probabilities)
    
    # choose next city best on probaility caclulations (i.e., pheromone trails and cost)
    def choose_next_city_probabilistic(self, visit_probabilities):
        accumulated_probability = 0.0
        rand_value = rand.uniform(0, 1)
        for i in range(len(visit_probabilities)):
            accumulated_probability += visit_probabilities[i]
            if accumulated_probability > rand_value:
                return i
        return len(visit_probabilities) - 1

    # choose next city to visit randomly
    def choose_next_city_random(self):
        choice = None
        while choice is None:
            # pick a random city and check if ant hasn't visited yet
            choice = rand.randint(0, self.problem.num_cities - 1)
            if self.has_visited(choice):
                choice = None
        return choice

class AntColony:
    def __init__(self, problem):
        self.problem = problem
        self.ants = []
        self.best_tour = None
        self.initialize_colony()
    
    def initialize_colony(self):
        # add one ant to colony per city in map
        self.ants = []
        for i in range (0, self.problem.num_cities):
            self.ants.append(Ant(self.problem))

    def solve_problem(self):
        for i in range(0, NUMBER_OF_ITERATIONS):
            for ant in self.ants:
                ant.tour_map(i)
            self.update_pheromones()
            self.save_best_tour()
            self.initialize_colony()
            print(self.best_tour)
        return self.best_tour
    
    def save_best_tour(self):
        for ant in self.ants:
            if self.best_tour is None:
                self.best_tour = (ant.visited_cities, ant.tour_length)
            elif ant.tour_length < self.best_tour[1]:
                self.best_tour = (ant.visited_cities, ant.tour_length)

    def update_pheromones(self):
        pheromone_trails = self.problem.pheromone_trails
        # reduce pheromone levels on all edges base give constant evaporation rate
        for i in range(0, self.problem.num_cities):
            for j in range(0, self.problem.num_cities):
                pheromone_trails[i][j] = pheromone_trails[i][j] * EVAPORATION_RATE
        # place each ant's pheromone on the edges it traveled in its touor
        for ant in self.ants:
            # calculate how much pheromone this ant places on each edge
            pheromone_amount = Q / ant.tour_length
            for i in range(0, len(ant.visited_cities) - 1):
                city_id = ant.visited_cities[i]
                # put pheromone on edge between current city and next city
                next_city_id = ant.visited_cities[i + 1]
                pheromone_trails[city_id][next_city_id] = pheromone_trails[city_id][next_city_id] + pheromone_amount

class Problem:
    def __init__(self, num_cities):
        self.map = Map(num_cities)
        self.num_cities = num_cities
        self.distance_matrix = []
        self.pheromone_trails = []
        self.start_city_id = None
        self.initialize()
    
    def initialize(self):
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
        for i in range(self.num_cities):
            temp_trail = []
            for j in range(self.num_cities):
                temp_trail.append(1)
            self.pheromone_trails.append(temp_trail)
        # randomly pick starting city
        self.start_city_id = rand.randint(0, self.num_cities - 1)

class NearestNeighborSolver:
    def __init__(self, problem):
        self.problem = problem
        self.visited_cities = []
        self.tour_length = 0

    def visit_city(self, city_id):
        self.visited_cities.append(city_id)
    
    def has_visited(self, city_id):
        return not city_id not in self.visited_cities

    def update_tour_length(self, current_city_id, city_id):
        self.tour_length += self.problem.distance_matrix[current_city_id][city_id]
    
    def solve(self):
        current_city_id = self.problem.start_city_id
        self.visit_city(self.problem.start_city_id)
        for i in range(0, self.problem.num_cities - 1):
            # choose next city to visit
            next_city_id = self.choose_nearest_neighbor(current_city_id)
            # visit city and update trail length
            self.visit_city(next_city_id)
            self.update_tour_length(current_city_id, next_city_id)
            current_city_id = next_city_id
        # when I have visited final city, go back to start, and update tour length?
        self.visit_city(self.problem.start_city_id)
        self.update_tour_length(current_city_id, self.problem.start_city_id)
        return (self.visited_cities, self.tour_length)
    
    def choose_nearest_neighbor(self, current_city_id):
        neighbor_distances = self.problem.distance_matrix[current_city_id]
        # array holding tuples of unvisited cities (city_id, distance to city)
        unvisited_distances = []
        for i in range(0, len(neighbor_distances)):
            if not self.has_visited(i):
                unvisited_distances.append((i, neighbor_distances[i]))
        # sort unvisited neighbors by distance
        sorted_neighbors = sorted(unvisited_distances, key=lambda x: x[1])
        # return id of first neighbor in list
        return sorted_neighbors[0][0]

def draw_map(problem, canvas):
    city_map = problem.map.cities
    for city_id in city_map:
        city = city_map[city_id]
        pt = Point(city.x, city.y)
        cir = Circle(pt, 25)
        cir.draw(canvas)
        if city_id == problem.start_city_id:
            color = 'blue'
        else:
            color = 'red'
        cir.setOutline(color)
        cir.setFill(color)

def draw_solution(tour, city_map, canvas):
    for i in range(0, len(tour) - 1):
        city1 = city_map[tour[i]]
        city2 = city_map[tour[i + 1]]
        line = Line(Point(city1.x, city1.y), Point(city2.x, city2.y))
        line.setFill('black')
        line.setOutline('black')
        line.draw(canvas)

def main():
    # generate problem with 10 cities
    problem = Problem(20)
    # Draw Cities
    draw_map(problem, win)
    draw_map(problem, win2)
    # create colony and give it the problem
    colony = AntColony(problem)
    # solve problem with colony
    print(colony.solve_problem())
    # Draw Solution
    draw_solution(colony.best_tour[0], problem.map.cities, win)
    # solve with nearest neighbor
    baseline_solver = NearestNeighborSolver(problem)
    print("Nearest Neighbor Solution: ")
    NNReturn = baseline_solver.solve()
    print(NNReturn[1])
    ##############################################
    draw_solution(NNReturn[0], problem.map.cities, win2)
    ##############################################
    win.getMouse()
    win.close()


main()
# problem = Problem(10)
# ant = Ant(problem)
# print(ant.choose_next_city(ant.calculate_probabilities(0)))
# problem = Problem(10)
# for x in range(len(problem.distance_matrix)):
#     for y in range(len(problem.distance_matrix)):
#         print(problem.distance_matrix[x][y], end=",", flush=True)
#     print()