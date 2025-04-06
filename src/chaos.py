import random

class ChaosHandler:
    def __init__(self, noise_level=0.25, dist_matrix=None):
        self.noise_level = noise_level
        self.dist_matrix = dist_matrix

    def chaos_two_opt(self, route, problem_data):
        if len(route) < 2:
            return route
        best = route[:]
        max_swaps = min(15, max(10, len(route) // 10))
        swaps = 0
        for _ in range(max_swaps * 10):
            i, j = random.sample(range(1, len(best) - 1), 2)
            if i > j:
                i, j = j, i
            if j - i < 2:
                continue
            delta = self.route_length(best[:i] + best[i:j][::-1] + best[j:], problem_data) - self.route_length(best, problem_data)
            if delta < 0:
                best = best[:i] + best[i:j][::-1] + best[j:]
                swaps += 1
                if swaps >= max_swaps:
                    break
        return best

    def route_length(self, route, problem_data):
        if len(route) < 2:
            return 0
        coords = [problem_data[i] for i in route]
        return sum(((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5 
                   for a, b in zip(coords[:-1], coords[1:])) + \
               ((coords[-1][0] - coords[0][0]) ** 2 + (coords[-1][1] - coords[0][1]) ** 2) ** 0.5
