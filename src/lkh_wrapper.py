# src/lkh_wrapper.py
# Note: Requires LKH library (http://akira.ruc.dk/~keld/research/LKH/)
from lkh import LKH

class ChaosLKH:
    def __init__(self, noise_level=0.1):
        self.noise_level = noise_level
        self.lkh = LKH()

    def polish(self, route, cities, max_swaps):
        problem = self.to_tsp_file(cities)
        best = route[:]
        for _ in range(3):  # 3 noise runs
            noisy_cities = [(x + random.uniform(-self.noise_level, self.noise_level),
                             y + random.uniform(-self.noise_level, self.noise_level))
                            for x, y in cities]
            result = self.lkh.solve(problem, initial_tour=best, max_trials=max_swaps)
            if self.route_length(result, noisy_cities) < self.route_length(best, noisy_cities):
                best = result
        return best

    def to_tsp_file(self, cities):
        # Simplified—real impl needs TSPLIB format
        return [(i, x, y) for i, (x, y) in enumerate(cities)]

    def route_length(self, route, cities):
        return sum(((cities[route[i]][0] - cities[route[i + 1]][0]) ** 2 + 
                    (cities[route[i]][1] - cities[route[i + 1]][1]) ** 2) ** 0.5 
                   for i in range(len(route) - 1)) + \
               ((cities[route[-1]][0] - cities[route[0]][0]) ** 2 + 
                (cities[route[-1]][1] - cities[route[0]][1]) ** 2) ** 0.5
