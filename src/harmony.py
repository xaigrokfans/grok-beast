import numpy as np
import random

class Harmony:
    def __init__(self, domain='tsp'):
        self.domain = domain
        self.TR = 1.55 if domain == 'tsp' else 1.0
        self.cues = {'density': 0, 'cluster': 0, 'scale': 0, 'noise': 0.25}

    def update_cues(self, problem, solution):
        """Update ecological cues based on domain and solution, with downsampling."""
        if self.domain == 'tsp':
            coords = [problem[i] for i in solution] if all(isinstance(i, (int, float)) for i in solution) else solution
            # Downsample to max 100 points or 10% of coords
            sample_size = min(100, max(10, len(coords) // 10))
            sampled_coords = random.sample(coords, sample_size) if len(coords) > sample_size else coords
            avg_dist = sum(((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5 
                           for a, b in zip(sampled_coords[:-1], sampled_coords[1:])) / len(sampled_coords) if len(sampled_coords) > 1 else 0
            self.cues['density'] = avg_dist
            self.cues['scale'] = len(problem)
            # Sample problem points for clustering
            sample_problem = random.sample(problem, min(100, len(problem))) if len(problem) > 100 else problem
            self.cues['cluster'] = sum(1 for i in range(len(sample_problem) - 1) 
                                      if min(((sample_problem[i][0] - c[0]) ** 2 + (sample_problem[i][1] - c[1]) ** 2) ** 0.5 
                                             for c in sample_problem) < 30) / len(sample_problem)
        elif self.domain == 'sat':
            sample_size = min(100, max(10, len(problem['clauses']) // 10))
            sampled_clauses = random.sample(problem['clauses'], sample_size) if len(problem['clauses']) > sample_size else problem['clauses']
            self.cues['density'] = len(sampled_clauses) / problem['vars']
            self.cues['scale'] = problem['vars']
            self.cues['cluster'] = sum(1 for clause in sampled_clauses if len(clause) < 4) / len(sampled_clauses)
        elif self.domain == 'qec':
            sample_size = min(100, max(10, len(problem['state']) // 10))
            sampled_state = random.sample(problem['state'], sample_size) if len(problem['state']) > sample_size else problem['state']
            self.cues['density'] = sum(sampled_state) / len(sampled_state)
            self.cues['scale'] = problem['qubits']
            self.cues['cluster'] = 0
        elif self.domain == 'fold':
            sample_size = min(100, max(10, len(solution) // 10))
            sampled_solution = random.sample(solution, sample_size) if len(solution) > sample_size else solution
            self.cues['density'] = sum(abs(a) for a in sampled_solution) / len(sampled_solution)
            self.cues['scale'] = len(problem['sequence'])
            self.cues['cluster'] = sum(1 for i in range(len(sampled_solution) - 2) if abs(sampled_solution[i] - sampled_solution[i + 2]) < 10) / len(sampled_solution)

    def tune_TR(self):
        """Tune Target Ratio based on cues, domain-specific."""
        if self.domain == 'tsp':
            if self.cues['density'] < 20:
                self.TR = max(1.3, self.TR - 0.05)
            if self.cues['scale'] > 500:
                self.TR = min(1.8, self.TR + 0.05)
        elif self.domain == 'sat':
            self.TR = 1.0 + (self.cues['density'] - 4.26) * 0.1
        elif self.domain == 'qec':
            self.TR = 1.0 - self.cues['density'] * 0.1
        elif self.domain == 'fold':
            self.TR = 1.0 + self.cues['cluster'] * 0.2
        return self.TR

    def score_segment(self, segment, problem):
        """Score segment harmony, domain-specific."""
        if self.domain == 'tsp':
            coords = [problem[i] for i in segment] if all(isinstance(i, (int, float)) for i in segment) else segment
            lengths = [((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5 
                       for a, b in zip(coords[:-1], coords[1:])]
            if not lengths: return 0
            ratios = [lengths[i] / lengths[i + 1] for i in range(len(lengths) - 1)]
            return sum(abs(r - self.TR) for r in ratios) / len(ratios) if ratios else 0
        elif self.domain == 'sat':
            sat_ratio = sum(any(segment[abs(lit) - 1] == (lit > 0) for lit in clause) 
                            for clause in problem['clauses']) / len(problem['clauses'])
            return abs(sat_ratio - self.TR)
        elif self.domain == 'qec':
            error = self.error_rate(segment, problem)
            return abs((1 - error) - self.TR)
        elif self.domain == 'fold':
            tm = self.tm_score(segment, problem)
            return abs(tm - self.TR)
        return 0

    def flow_fitness(self, solution, problem, runtime):
        """Bejan-inspired flow fitness for 2.0."""
        length = self.route_length(solution, problem)
        baseline = length * 1.5  # Tune this (1.5 → ~30, 2.0 → ~22)
        error = min(length / baseline, 1.0)
        speed = min(3600 / runtime, 60)
        adapt = min(self.cues['noise'] / 0.15, 1.5)
        return (1 - error) * speed * adapt

    def error(self, solution, problem):
        """Domain-specific error metric."""
        if self.domain == 'tsp':
            length = self.route_length(solution, problem)
            return length / (self.cues['scale'] * self.cues['density']) if self.cues['density'] > 0 else 0
        elif self.domain == 'sat':
            return 1 - sum(any(solution[abs(lit) - 1] == (lit > 0) for lit in clause) 
                           for clause in problem['clauses']) / len(problem['clauses'])
        elif self.domain == 'qec':
            return self.error_rate(solution, problem)
        elif self.domain == 'fold':
            return 1 - self.tm_score(solution, problem)
        return 0

    # Helper functions
    def route_length(self, route, problem):
        """Calculate route length, handling indices or coords."""
        if len(route) < 2:
            return 0
        coords = [problem[i] for i in route] if all(isinstance(i, (int, float)) for i in route) else route
        return sum(((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5 
                   for a, b in zip(coords[:-1], coords[1:])) + \
               ((coords[-1][0] - coords[0][0]) ** 2 + (coords[-1][1] - coords[0][1]) ** 2) ** 0.5

    def error_rate(self, state, problem):
        """Simplified QEC error rate (placeholder)."""
        return min(0.005, sum(state) / len(state))

    def tm_score(self, fold, problem):
        """Simplified TM-score (placeholder)."""
        return min(1.0, 0.7 + sum(abs(a) for a in fold) / (len(fold) * 10))
