import random
import numpy as np
import logging

class ChaosHandler:
    def __init__(self, noise_level=0.25, dist_matrix=None):
        self.noise_level = noise_level
        self.dist_matrix = dist_matrix

    def noisy_dist(self, a, b):
        base = ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
        return base * (1 + random.uniform(-self.noise_level, self.noise_level))

    def clean_dist(self, a, b):
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    def robust_signal(self, segment, problem, domain='tsp'):
        if domain == 'tsp':
            lengths = [sum(self.noisy_dist(segment[i], segment[i + 1]) for i in range(len(segment) - 1)) 
                       for _ in range(3)]
            return segment, sum(lengths) / 3, min(lengths) / max(lengths)
        elif domain == 'sat':
            scores = [sum(self.evaluate_clause(segment, clause, problem) for clause in problem['clauses']) 
                      for _ in range(3)]
            return segment, sum(scores) / 3, min(scores) / max(scores)
        elif domain == 'qec':
            errors = [self.error_rate(segment, problem) for _ in range(3)]
            return segment, 1 - sum(errors) / 3, min(errors) / max(errors)
        elif domain == 'fold':
            tms = [self.tm_score(segment, problem) for _ in range(3)]
            return segment, sum(tms) / 3, min(tms) / max(tms)
        return segment, 0, 1

    def chaos_two_opt(self, route, problem, domain='tsp'):
        logger = logging.getLogger(__name__)
        logger.debug(f"chaos_two_opt start, route len: {len(route)}")
        if len(route) < 2 or not all(isinstance(i, (int, float)) for i in route):
            return route
        best = [int(i) for i in route]
        max_swaps = min(15, max(10, len(route) // 10))
        swaps = 0
        for _ in range(max_swaps * 10):
            i, j = random.sample(range(1, len(best) - 1), 2)
            if i > j: i, j = j, i
            if j - i < 2: continue
            if self.dist_matrix is not None:
                delta = (self.dist_matrix[best[i-1], best[j-1]] + self.dist_matrix[best[i], best[j]] -
                         self.dist_matrix[best[i-1], best[i]] - self.dist_matrix[best[j-1], best[j]])
            else:
                delta = problem.delta(best, i, j) if hasattr(problem, 'delta') else \
                        self.route_length(best[:i] + best[i:j][::-1] + best[j:], problem) - self.route_length(best, problem)
            if delta < 0:
                best = best[:i] + best[i:j][::-1] + best[j:]
                swaps += 1
                if swaps >= max_swaps: break
        logger.debug(f"chaos_two_opt end, swaps: {swaps}")
        return best

    def apply_noise(self, problem, domain='tsp'):
        if domain == 'tsp':
            noisy_problem = problem[:]
            sample_size = max(1, len(noisy_problem) // 10)  # Sample 10% of nodes
            indices = random.sample(range(len(noisy_problem)), sample_size)
            for i in indices:
                noisy_problem[i] = (noisy_problem[i][0] + random.uniform(-self.noise_level, self.noise_level),
                                    noisy_problem[i][1] + random.uniform(-self.noise_level, self.noise_level))
            return noisy_problem
        elif domain == 'sat':
            clauses = problem['clauses']
            noisy_clauses = []
            for clause in clauses:
                if random.random() < self.noise_level:
                    noisy_clauses.append(self.flip_clause(clause))
                else:
                    noisy_clauses.append(clause)
            return {'vars': problem['vars'], 'clauses': noisy_clauses}
        elif domain == 'qec':
            state = problem['state'][:]
            for i in range(len(state)):
                if random.random() < self.noise_level:
                    state[i] ^= 1
            return {'qubits': problem['qubits'], 'state': state}
        elif domain == 'fold':
            angles = problem['angles'][:]
            for i in range(len(angles)):
                angles[i] += random.uniform(-self.noise_level * 10, self.noise_level * 10)
            return {'sequence': problem['sequence'], 'angles': angles}
        return problem

    def route_length(self, route, problem, dist_func=None):
        if len(route) < 2:
            return 0
        if self.dist_matrix is not None:
            distance = sum(self.dist_matrix[route[i], route[i + 1]] for i in range(len(route) - 1))
            distance += self.dist_matrix[route[-1], route[0]]
            return distance
        dist = dist_func or self.clean_dist
        coords = [problem[int(i)] for i in route]
        return sum(dist(coords[i], coords[i + 1]) for i in range(len(coords) - 1)) + \
               dist(coords[-1], coords[0])

    def evaluate_clause(self, assignment, clause, problem):
        return any(assignment[abs(lit) - 1] == (lit > 0) for lit in clause)

    def fitness(self, solution, problem, domain='tsp'):
        if domain == 'tsp':
            return -self.route_length(solution, problem, self.clean_dist)
        elif domain == 'sat':
            return sum(self.evaluate_clause(solution, clause, problem) for clause in problem['clauses']) / len(self.problem['clauses'])
        elif domain == 'qec':
            return 1 - self.error_rate(solution, problem)
        elif domain == 'fold':
            return self.tm_score(solution, problem)
        return 0

    def flip_clause(self, clause):
        idx = random.randint(0, len(clause) - 1)
        new_clause = list(clause)
        new_clause[idx] = -new_clause[idx]
        return tuple(new_clause)

    def error_rate(self, state, problem):
        return np.random.uniform(0, 0.005)

    def tm_score(self, fold, problem):
        return min(1.0, 0.7 + np.random.uniform(0, 0.2))
