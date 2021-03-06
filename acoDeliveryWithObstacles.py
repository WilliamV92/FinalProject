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
# Obstacle (i.e., Disaster) Parameters
DISASTER_RATE = 0.2
DISASTER_MODE = False
# Delivery Parameters
TRUCK_CAPACITY = 10 # how many units a truck can hold
MAX_CITY_NEED = TRUCK_CAPACITY * 0.5 # the max need in units a particular city can have
# UI 
DISPLAY_WIDTH = 600
DISPLAY_HEIGHT = 800
drawn_lines = []
drawn_lines2 = []
message = None
win = GraphWin(title="ACO", width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)
win2 = GraphWin(title="Nearest Neighbor", width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)

class Map:
    def __init__(self, city_count, max_city_need):
        self.city_count = city_count
        self.max_city_need = max_city_need
        self.cities = self.generate_cities()
    
    def generate_cities(self):
        cities = {}
        existing_cities = set()
        while len(existing_cities) != self.city_count:
            x = rand.randint(50, DISPLAY_WIDTH - 50)
            y = rand.randint(50, DISPLAY_HEIGHT - 50)
            if not self.check_if_nearby_city_exists(existing_cities, (x, y)):
                existing_cities.add((x, y))
        for i in range(len(existing_cities)):
            city_need = rand.randint(1, self.max_city_need)
            new_city = City(existing_cities.pop(), i, city_need)
            cities[i] = new_city
        return cities
    
    def check_if_nearby_city_exists(self, existing_cities, coords):
        nearby_exits = False
        for city in existing_cities:
            if math.hypot(city[0] - coords[0], city[1] - coords[1]) <= 50:
                nearby_exits = True
                break
        return nearby_exits

    def get_city_need(self, city_id):
        return self.cities[city_id].need

    def display_cities(self):
        for city in self.cities:
            print(self.cities[city])

class City():
    def __init__(self, coords, id, need):
        self.x = coords[0]
        self.y = coords[1]
        self.need = need
        self.id = id
    def distance_from(self, city):
        return math.hypot(city.x - self.x, city.y -self.y)
    def __str__(self):
        return("ID: {0} X: {1} Y: {2} Need: {3}".format(self.id, self.x, self.y, self.need))

class Ant:
    def __init__(self, problem):
        self.problem = problem
        self.capacity = problem.truck_capacity
        self.visited_cities = []
        self.visit_total = 0
        self.tour_length = 0

    def visit_city(self, city_id):
        # keep track of how many of the cities any has visited
        if city_id not in self.visited_cities:
            self.visit_total += 1
        # add city to tour
        self.visited_cities.append(city_id)
        # drop off goods at city or pick up from depot
        if city_id != self.problem.start_city_id:
            # drop off goods at the city
            self.capacity -= self.problem.map.get_city_need(city_id)
        elif len(self.visited_cities) > 1:
            # we are returning to the depot, fill the truck back to its capacity
            self.capacity = self.problem.truck_capacity
    
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
        while self.visit_total < self.problem.num_cities:
            # determine probability to travel to each city from current city
            visit_probailities = self.calculate_probabilities(current_city_id)
            # choose next city to visit
            next_city_id = self.choose_next_delivery(current_city_id, visit_probailities, iteration)
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
            # if city has been visited or the current city, visit probaility is zero.
            if i not in self.visited_cities and i != current_city_id:
                edge_pheromone = math.pow(self.problem.pheromone_trails[current_city_id][i], ALPHA)
                edge_cost = math.pow(1.0 / self.problem.distance_matrix[current_city_id][i], BETA)
                # this calculation is used below as well. saving for later use
                edge_scores.append(edge_pheromone * edge_cost)
                pheromone_total += edge_scores[i]
            else:
                edge_scores.append(0)

        for i in range(self.problem.num_cities):
            if edge_scores[i] == 0:
                visit_probabilities.append(0)
            else:
                visit_probabilities.append(edge_scores[i] / pheromone_total)
        return visit_probabilities

    def choose_next_delivery(self, current_city_id, visit_probabilities, iteration):
         # determine next city to visit based on normal distance minimization logic
        next_city_id = self.choose_next_city(visit_probabilities, iteration)
        # check if ant has capacity to deliver to this city, if not, return to depot
        if self.capacity >= self.problem.map.get_city_need(next_city_id):
            # deliver to city
            return next_city_id
        else:
            # decide whether to go back to depot or find another city to deliver to
            return self.find_viable_close_city(current_city_id, visit_probabilities)
    
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
            if accumulated_probability >= rand_value:
                return i
        return self.choose_next_city_random()

    # choose next city to visit randomly
    def choose_next_city_random(self):
        choice = None
        while choice is None:
            # pick a random city and check if ant hasn't visited yet
            choice = rand.randint(0, self.problem.num_cities - 1)
            if self.has_visited(choice):
                choice = None
        return choice
    
    def find_viable_close_city(self, current_city_id, visit_probabilities):
        # get distances from current_city to all other cities
        neighbor_distances = self.problem.distance_matrix[current_city_id]
        # array holding tuples of unvisited cities (city_id, distance to city)
        unvisited_distances = []
        for i in range(0, len(neighbor_distances)):
            if not self.has_visited(i):
                unvisited_distances.append((i, neighbor_distances[i]))
        # sort unvisited neighbors by distance
        sorted_neighbors = sorted(unvisited_distances, key=lambda x: x[1])
        # get distance from current depot to city
        distance_to_depot = self.problem.distance_matrix[current_city_id][self.problem.start_city_id]
        for i in range(0, len(sorted_neighbors)):
            option = sorted_neighbors[i]
            if option[1] <= distance_to_depot and self.capacity >= self.problem.map.get_city_need(option[0]):
                # found a city that is closer to current city than depot and
                # truck has the capacity currently to deliver to it
                return option[0]
        # no option was found better than returning to the depot itself
        return self.problem.start_city_id

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
        global NUMBER_OF_ITERATIONS
        i = 0
        while i < NUMBER_OF_ITERATIONS:
            fade_lines()
            if DISASTER_MODE:
                was_disaster = self.problem.generate_disaster(i, self.best_tour)
                if was_disaster:
                    self.best_tour = None
                    NUMBER_OF_ITERATIONS += 5             
            for ant in self.ants:
                ant.tour_map(i)
            self.update_pheromones()
            self.save_best_tour()
            self.initialize_colony()
            draw_solution(self.best_tour, self.problem.map.cities, win, self.problem)
            i += 1
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
    def __init__(self, num_cities, truck_capcity, max_city_need):
        self.map = Map(num_cities, max_city_need)
        self.num_cities = num_cities
        self.truck_capacity = truck_capcity
        self.max_city_need = max_city_need
        self.distance_matrix = []
        self.pheromone_trails = []
        self.blocked_edges = []
        self.start_city_id = None
        self.blocked_edges = []
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
        # randomly pick starting city (depot)
        self.start_city_id = rand.randint(0, self.num_cities - 1)
        self.map.cities[self.start_city_id].need = 0
    
    def generate_disaster(self, iteration, current_path):
        was_disaster = False
        # determine if there should be a random disaster
        if self.is_disaster(iteration):
            current_path = current_path[0]
            # determine edge between two cities in current path to block
            rand_index = rand.randint(0, len(current_path) - 2)
            city1_id = current_path[rand_index]
            city2_id = current_path[rand_index + 1]
            self.blocked_edges.append((city1_id, city2_id))
            print("disaster: " + str(city1_id) + " " + str(city2_id))
            # increase distance score between city1 to city2 to indicate it is impassibe
            self.distance_matrix[city1_id][city2_id] = sys.maxsize
            self.distance_matrix[city2_id][city1_id] = sys.maxsize
            was_disaster = True
            draw_blocked(city1_id, city2_id, self.map.cities, win)
            draw_blocked(city1_id, city2_id, self.map.cities, win2)
        return was_disaster

    def is_disaster(self, iteration):
        disaster = False
        if iteration > 2 and len(self.blocked_edges) < self.num_cities * 0.2:
            rand_num = rand.uniform(0, 1)
            if rand_num < DISASTER_RATE:
                disaster = True
        return disaster

class NearestNeighborSolver:
    def __init__(self, problem):
        self.problem = problem
        self.capacity = problem.truck_capacity
        self.visit_total = 0
        self.visited_cities = []
        self.tour_length = 0

    def visit_city(self, city_id):
         # keep track of how many of the cities any has visited
        if city_id not in self.visited_cities:
            self.visit_total += 1
        # add city to tour
        self.visited_cities.append(city_id)
        # drop off goods at city or pick up from depot
        if city_id != self.problem.start_city_id:
            # drop off goods at the city
            self.capacity -= self.problem.map.get_city_need(city_id)
        elif len(self.visited_cities) > 1:
            # we are returning to the depot, fill the truck back to its capacity
            self.capacity = self.problem.truck_capacity
    
    def has_visited(self, city_id):
        return not city_id not in self.visited_cities

    def update_tour_length(self, current_city_id, city_id):
        self.tour_length += self.problem.distance_matrix[current_city_id][city_id]
    
    def solve(self):
        current_city_id = self.problem.start_city_id
        self.visit_city(self.problem.start_city_id)
        while self.visit_total < self.problem.num_cities:
            # choose next city to visit
            next_city_id = self.choose_next_delivery(current_city_id)
            # visit city and update trail length
            self.visit_city(next_city_id)
            self.update_tour_length(current_city_id, next_city_id)
            current_city_id = next_city_id
        # when I have visited final city, go back to start, and update tour length?
        self.visit_city(self.problem.start_city_id)
        self.update_tour_length(current_city_id, self.problem.start_city_id)
        return (self.visited_cities, self.tour_length)
    
    def choose_next_delivery(self, current_city_id):
        nearest_neighbor = self.choose_nearest_neighbor(current_city_id)
        if self.capacity >= self.problem.map.get_city_need(nearest_neighbor):
            # deliver to city
            return nearest_neighbor
        else:
            # decide whether to go back to depot or find another city to deliver to
            return self.problem.start_city_id

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
    inc = 0
    for city_id in city_map:
        # message = Text()
        city = city_map[city_id]
        pt = Point(city.x, city.y)
        cir = Circle(pt, 25)
        cir.draw(canvas)
        message = Text(pt, "{0}\n({1})".format(inc, city.need))
        message.draw(canvas)
        if city_id == problem.start_city_id:
            color = 'blue'
        else:
            color = 'red'
        cir.setOutline(color)
        cir.setFill(color)
        inc += 1

def draw_solution(tour, city_map, canvas, problem):
    global message
    path = tour[0]
    if type(message) == Text:
        message.undraw()
    message = Text(Point(canvas.getWidth() / 2, 20), "Path: {0}\nCost: {1:.0f}".format(tour[0], tour[1]))
    message.draw(canvas)
    chkMouse = canvas.checkMouse()
    getMouse = None
    for i in range(0, len(path) - 1):
        while(chkMouse != None and getMouse == None):
            getMouse = canvas.getMouse()
        city1 = city_map[path[i]]
        city2 = city_map[path[i + 1]]
        line = Line(Point(city1.x, city1.y), Point(city2.x, city2.y))
        line.setFill('black')
        line.setOutline('black')
        line.setWidth(2)
        line.draw(canvas)
        drawn_lines.append(line)
        time.sleep(.25)
        chkMouse = canvas.checkMouse()
        getMouse = None
    draw_map(problem, canvas)

def fade_lines():
    global drawn_lines
    global drawn_lines2
    for line in drawn_lines2:
        line.undraw()
    for line in drawn_lines:
        line.setFill('grey')
        line.setOutline('grey')
    drawn_lines2 = drawn_lines.copy()
    drawn_lines.clear()

def draw_blocked(city1, city2, city_map, canvas):
    pt1 = city_map[city1]
    pt2 = city_map[city2]
    line = Line(Point(pt1.x, pt1.y), Point(pt2.x, pt2.y))
    line.setFill('red')
    line.setOutline('red')
    line.setWidth(2)
    line.draw(canvas)

def main():
    # generate problem with 10 cities
    problem = Problem(20, TRUCK_CAPACITY, MAX_CITY_NEED)
    problem.map.display_cities()
    # Draw Cities
    draw_map(problem, win)
    draw_map(problem, win2)
    # create colony and give it the problem
    colony = AntColony(problem)
    # solve problem with colony
    print(colony.solve_problem())
    # solve with nearest neighbor
    baseline_solver = NearestNeighborSolver(problem)
    print("Nearest Neighbor Solution: ")
    NNReturn = baseline_solver.solve()
    print(NNReturn[1])
    ##############################################
    draw_solution(NNReturn, problem.map.cities, win2, problem)
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