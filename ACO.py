import random as rand

def generate_matrix(no_cities):
    cities = []
    for i in range(no_cities):
        row = []
        for j in range(no_cities):
            row.append(rand.randint(0, 1))
        cities.append(row)
    return cities

def generate_trails(city_matrix):
    city_count = len(city_matrix)
    trails = []
    for i in range(city_count):
        row = []
        for j in range(city_count):
            if(city_matrix[i][j] == 1):
                row.append(rand.randint(0, 100))
            else:
                row.append(0)
        trails.append(row)
    return trails

city_matrix = generate_matrix(10)
trail_matrix = generate_trails(city_matrix)
print(city_matrix)
print(trail_matrix)