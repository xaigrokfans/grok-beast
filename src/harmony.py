import numpy as np

class Harmony:
    def __init__(self, domain='tsp'):
        self.domain = domain
        self.TR = 1.55 if domain == 'tsp' else 1.0
        self.cues = {'density': 0, 'cluster': 0, 'scale': 0, 'noise': 0.25}

    def update_cues(self, problem_data, solution):
        if self.domain == 'tsp':
            coords = [problem_data[i] for i in solution]
            avg_dist = sum(((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5 
                           for a, b in zip(coords[:-1], coords[1:])) / len(coords) if len(coords) > 1 else 0
            self.cues['density'] = avg_dist
            self.cues['scale'] = len(problem_data)

    def tune_TR(self):
        if self.domain == 'tsp':
            if self.cues['density'] < 20:
                self.TR = max(1.3, self.TR - 0.05)
            if self.cues['scale'] > 500:
                self.TR = min(1.8, self.TR + 0.05)
        return self.TR

    def flow_fitness(self, solution, problem_data, runtime):
        length = self.route_length(solution, problem_data)
        baseline = length * 1.5
        error = min(length / baseline, 1.0)
        speed = min(3600 / runtime, 60)
        adapt = min(self.cues['noise'] / 0.15, 1.5)
        return (1 - error) * speed * adapt

    def route_length(self, route, problem_data):
        if len(route) < 2:
            return 0
        coords = [problem_data[i] for i in route]
        return sum(((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5 
                   for a, b in zip(coords[:-1], coords[1:])) + \
               ((coords[-1][0] - coords[0][0]) ** 2 + (coords[-1][1] - coords[0][1]) ** 2) ** 0.5
