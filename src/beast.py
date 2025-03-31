import numpy as np
from random import choice, random, shuffle, sample
from elm import ELM
import logging
import time
import random

class Beast:
    def __init__(self, role='local', tribe_id=0, domain='tsp', dist_matrix=None):
        """Initialize the Beast with role, tribe, domain, and optional distance matrix."""
        np.random.seed(42)
        self.role = role
        self.tribe_id = tribe_id
        self.domain = domain
        self.solution = []
        self.instincts = {
            'tsp': {'2-opt': 0.0, 'cluster': 0.4, 'nn': 0.6},
            'sat': {'flip': 0.6, 'cluster': 0.3, 'random': 0.1},
            'qec': {'parity': 0.5, 'reroute': 0.3, 'reset': 0.2},
            'fold': {'helix': 0.4, 'sheet': 0.3, 'random': 0.3}
        }.get(domain, {'2-opt': 0.5})
        self.signals = []
        self.epigenetic_tags = {}
        self.elm_rules = []
        self.fitness_history = []
        self.problem = None
        self.dist_matrix = dist_matrix

    def dist(self, a, b):
        """Calculate distance between two points using dist_matrix if available."""
        return self.dist_matrix[a, b] if self.dist_matrix is not None else \
               np.sqrt((self.problem[a][0] - self.problem[b][0])**2 + 
                       (self.problem[a][1] - self.problem[b][1])**2)

    def instinct_seed(self, problem, gen):
        """Generate an initial solution based on domain and generation."""
        logger = logging.getLogger(__name__)
        logger.debug(f"[Beast.instinct_seed]with problem size: {len(problem)}")
        if self.problem is None or len(self.problem) != len(problem):
            self.problem = np.array(problem)
            if self.domain == 'tsp' and self.dist_matrix is None:
                n_cities = len(problem)
                self.dist_matrix = np.zeros((n_cities, n_cities))
                for i in range(n_cities):
                    for j in range(i + 1, n_cities):
                        dist = np.sqrt((self.problem[i][0] - self.problem[j][0])**2 + 
                                       (self.problem[i][1] - self.problem[j][1])**2)
                        self.dist_matrix[i, j] = self.dist_matrix[j, i] = dist
        if self.domain == 'tsp':
            n_cities = len(problem)
            if n_cities == 0:
                raise ValueError("No cities in TSP problem")
            indices = list(range(n_cities))
            if gen % 5 == 0:  # Shuffle every 5 gens
                shuffle(indices)
            logger.debug("[Beast.instinct_seed]Using periodic shuffle")
            return indices
        elif self.domain == 'sat':
            vars = problem['vars']
            return [choice([True, False]) for _ in range(vars)]
        elif self.domain == 'qec':
            qubits = problem['qubits']
            return [0] * qubits
        elif self.domain == 'fold':
            sequence = problem['sequence']
            return [0.0] * (len(sequence) * 2)

    def fractal_swap(self, solution, signals):
        """Perform fractal swap on solution segments based on signal fitness."""
        depth = min(5, len(solution) // 10)
        chunk_size = max(1, len(solution) // depth)
        solution_set = set(solution)
        for i in range(0, len(solution), chunk_size):
            chunk = solution[i:i + chunk_size]
            best_signal = max(signals, key=lambda s: s[1], default=(chunk, 0, 0))
            signal_seg = best_signal[0]
            if len(signal_seg) == len(chunk) and set(signal_seg).issubset(solution_set):
                if self.fitness(signal_seg) > self.fitness(chunk):
                    solution[i:i + chunk_size] = signal_seg
        return solution

    def evaluate_state(self, problem):
        """Evaluate current problem state for meme selection with sampling for cluster calculation.

        Optimizes performance by sampling a subset of coordinates (max 100) to calculate cluster count,
        reducing complexity from O(n²) to O(k²) where k is the sample size.
        """
        if self.domain == 'tsp':
            coords = [problem[i] for i in self.solution]
            if len(coords) < 2:
                return {'density': 'low', 'cluster': 'low'}
            # Calculate average distance (density)
            avg_dist = sum(((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5 
                           for a, b in zip(coords[:-1], coords[1:])) / (len(coords) - 1)
            # Sample up to 100 points for cluster calculation
            sample_size = min(100, len(coords))
            sampled_coords = random.sample(coords, sample_size)
            cluster_count = sum(1 for i in range(sample_size) 
                                for j in range(i + 1, sample_size) 
                                if ((sampled_coords[i][0] - sampled_coords[j][0]) ** 2 + 
                                    (sampled_coords[i][1] - sampled_coords[j][1]) ** 2) ** 0.5 < 30) / sample_size
            density = 'low' if avg_dist < 15 else 'medium' if avg_dist < 25 else 'high'
            cluster = 'low' if cluster_count < 0.3 else 'medium' if cluster_count < 0.7 else 'high'
            return {'density': density, 'cluster': cluster}
        return {}

    def select_meme(self, memes, current_state):
        """Select the best meme based on current state."""
        if not memes or not current_state:
            return None
        best_meme = None
        best_score = -1
        for meme in memes:
            if isinstance(meme, tuple):  # Skip legacy memes
                continue
            score = sum(1 for key, value in meme['conditions'].items() 
                        if current_state.get(key) == value)
            if score > best_score:
                best_score = score
                best_meme = meme
        return best_meme

    def apply_strategy(self, strategy):
        """Apply the selected strategy to the solution."""
        if self.domain == 'tsp' and strategy == '2-opt':
            self.solution = self.two_opt(self.solution)
        # Add more strategies for other domains as needed

    def two_opt(self, route):
        """Simple 2-opt optimization for TSP."""
        best = route[:]
        improved = True
        while improved:
            improved = False
            for i in range(1, len(best) - 2):
                for j in range(i + 2, len(best)):
                    if j - i == 1: continue
                    if self.dist(best[i - 1], best[j - 1]) + self.dist(best[i], best[j]) < \
                       self.dist(best[i - 1], best[i]) + self.dist(best[j - 1], best[j]):
                        best[i:j] = best[i:j][::-1]
                        improved = True
            break  # Limit to one pass for efficiency
        return best

    def evolve(self, problem, signals, memes, gen, noise_level=0.25, culture=None, use_cultural_signals=False):
        """Evolve the beast with dynamic meme application, skipping cultural signals in early gens."""
        logger = logging.getLogger(__name__)
        start = time.time()
        self.problem = problem
        self.solution = self.instinct_seed(problem, gen)
        if not self.solution:
            self.solution = list(range(len(problem)))

        # Skip cultural signals in early generations (Gen < 5)
        if use_cultural_signals and gen >= 5 and memes:
            # Exploit best meme based on current state
            current_state = self.evaluate_state(problem)
            selected_meme = self.select_meme(memes, current_state)
            if selected_meme:
                pre_fitness = self.fitness(self.solution)
                self.apply_strategy(selected_meme['strategy'])
                post_fitness = self.fitness(self.solution)
                improvement = post_fitness - pre_fitness
                if culture and improvement > 0:
                    culture.update_from_beast(selected_meme['strategy'], current_state, improvement, self.domain)

        # Existing evolution steps
        if len(problem) >= 100:
            elm = ELM(self.domain)
            elm.apply_rules(self, gen, noise_level)
        segments = self.extract_segments(self.solution)
        self.signals = [(s, self.fitness(s), self.epigenetic_tags.get(tuple(s), 0))
                        for s in sample(segments, min(10, len(segments)))]
        if len(problem) >= 100 and self.solution and gen % 2 == 0 and gen > 0:  # Every other gen
            logger.debug(f"[Beast.evolve]Gen {gen}, Tribe {self.tribe_id}, Beast {self.role} entering fractal_swap")
            self.solution = self.fractal_swap(self.solution, signals)
            logger.debug(f"[Beast.evolve]Gen {gen}, Tribe {self.tribe_id}, Beast {self.role} fractal_swap done")
        if len(set(self.solution)) != len(problem):
            self.solution = list(range(len(problem)))
        self.fitness_history.append(self.fitness(self.solution))
        logger.debug(f"[Beast.evolve]Gen {gen}, Tribe {self.tribe_id}, Beast {self.role} evolve end took {time.time() - start:.2f}s")
        return self.solution

    def evolve_try_signals_optims(self, problem, signals, memes, gen, noise_level=0.25, culture=None):
        """Evolve the beast with dynamic meme application."""
        logger = logging.getLogger(__name__)
        start = time.time()
        self.problem = problem
        self.solution = self.instinct_seed(problem, gen)
        if not self.solution:
            self.solution = list(range(len(problem)))

        # Early exploration or no memes: try a random strategy
        if gen < 5 or not memes:
            strategy = random.choice(list(self.instincts.keys()))
            pre_fitness = self.fitness(self.solution)
            self.apply_strategy(strategy)
            post_fitness = self.fitness(self.solution)
            improvement = post_fitness - pre_fitness
            current_state = self.evaluate_state(problem)
            if culture and improvement > 0:
                culture.update_from_beast(strategy, current_state, improvement, self.domain)
        else:
            # Exploit best meme based on current state
            current_state = self.evaluate_state(problem)
            selected_meme = self.select_meme(memes, current_state)
            if selected_meme:
                pre_fitness = self.fitness(self.solution)
                self.apply_strategy(selected_meme['strategy'])
                post_fitness = self.fitness(self.solution)
                improvement = post_fitness - pre_fitness
                if culture and improvement > 0:
                    culture.update_from_beast(selected_meme['strategy'], current_state, improvement, self.domain)

        # Existing evolution steps
        if len(problem) >= 100:
            elm = ELM(self.domain)
            elm.apply_rules(self, gen, noise_level)
        segments = self.extract_segments(self.solution)
        self.signals = [(s, self.fitness(s), self.epigenetic_tags.get(tuple(s), 0))
                        for s in sample(segments, min(10, len(segments)))]
        if len(problem) >= 100 and self.solution and gen % 2 == 0:  # Every other gen
            logger.debug(f"[Beast.evolve]Gen {gen}, Tribe {self.tribe_id}, Beast {self.role} entering fractal_swap")
            self.solution = self.fractal_swap(self.solution, signals)
            logger.debug(f"[Beast.evolve]Gen {gen}, Tribe {self.tribe_id}, Beast {self.role} fractal_swap done")
        if len(set(self.solution)) != len(problem):
            self.solution = list(range(len(problem)))
        self.fitness_history.append(self.fitness(self.solution))
        logger.debug(f"[Beast.evolve]Gen {gen}, Tribe {self.tribe_id}, Beast {self.role} evolve end took {time.time() - start:.2f}s")
        return self.solution

    def apply_memes(self, memes):
        """Legacy method for instinct adjustment."""
        if memes and memes[0][1] > 0.1:
            action = memes[0][0]
            if action in self.instincts:
                self.instincts[action] = min(1.0, self.instincts[action] + 0.1)

    def apply_elm_rules(self, problem, gen, noise_level):
        """Apply ELM rules to the solution."""
        for rule in self.elm_rules:
            if self.check_condition(rule['condition'], problem, gen, noise_level):
                self.execute_action(rule['actions'], problem)
        if random() < 0.1:
            new_rule = self.generate_elm_rule(problem, gen)
            self.elm_rules.append(new_rule)

    def check_condition(self, condition, problem, gen, noise_level):
        """Check if an ELM rule condition is met."""
        if 'noise >' in condition:
            thresh = float(condition.split('>')[1])
            return noise_level > thresh
        elif 'gen >' in condition:
            thresh = int(condition.split('>')[1])
            return gen > thresh
        return True

    def execute_action(self, actions, problem):
        """Execute an ELM rule action."""
        for action in actions:
            if self.domain == 'tsp' and action == '4-opt':
                self.solution = self.four_opt(self.solution)
            elif self.domain == 'sat' and action == 'flip':
                idx = np.random.randint(len(self.solution))
                self.solution[idx] = not self.solution[idx]
            elif self.domain == 'fold' and action == 'adjust phi/psi':
                idx = np.random.randint(0, len(self.solution), 2)
                self.solution[idx[0]] += np.random.uniform(-10, 10)

    def generate_elm_rule(self, problem, gen):
        """Generate a new ELM rule."""
        conditions = [f'noise > {random():.1f}', f'gen > {gen + 5}']
        actions = {
            'tsp': ['4-opt', 'core swaps'],
            'sat': ['flip', 'cluster'],
            'qec': ['parity', 'reroute'],
            'fold': ['adjust phi/psi', 'cluster cores']
        }.get(self.domain, ['2-opt'])
        return {'condition': choice(conditions), 'actions': [choice(actions)]}

    def four_opt(self, route):
        """Perform 4-opt optimization on the route."""
        best = route[:]
        for i in range(1, len(best) - 3):
            for j in range(i + 1, len(best) - 2):
                for k in range(j + 1, len(best) - 1):
                    for l in range(k + 1, len(best)):
                        new_route = best[:i] + best[i:j][::-1] + best[j:k] + best[k:l][::-1] + best[l:]
                        if self.route_length(new_route) < self.route_length(best):
                            best = new_route
        return best

    def route_length(self, route):
        """Calculate the total length of a TSP route."""
        if len(route) < 2:
            return float('inf')
        if self.dist_matrix is not None:
            indices = np.array(route)
            return np.sum(self.dist_matrix[indices[:-1], indices[1:]]) + self.dist_matrix[indices[-1], indices[0]]
        distance = sum(self.dist(route[i], route[i + 1]) for i in range(len(route) - 1))
        distance += self.dist(route[-1], route[0])
        return distance

    def fitness(self, solution):
        """Calculate the fitness of a solution based on domain."""
        if self.domain == 'tsp':
            return -self.route_length(solution)
        elif self.domain == 'sat':
            return sum(self.evaluate_clause(solution, clause) for clause in self.problem['clauses']) / len(self.problem['clauses'])
        elif self.domain == 'qec':
            return 1 - self.error_rate(solution, self.problem)
        elif self.domain == 'fold':
            return self.tm_score(solution, self.problem)
        return 0

    def evaluate_clause(self, assignment, clause):
        """Evaluate a SAT clause with the given assignment."""
        return any(assignment[abs(lit) - 1] == (lit > 0) for lit in clause)

    def error_rate(self, state, problem):
        """Simulate error rate for QEC domain."""
        return np.random.uniform(0, 0.005)

    def tm_score(self, fold, problem):
        """Simulate TM-score for protein folding domain."""
        return min(1.0, 0.7 + np.random.uniform(0, 0.2))

    def extract_segments(self, solution):
        """Extract segments from the solution for signal generation."""
        chunk_size = 10 if self.domain in ['tsp', 'sat'] else 10
        return [solution[i:i + chunk_size] for i in range(0, len(solution) - chunk_size + 1)]

    def flow_fitness(self, runtime, noise_level):
        """Calculate flow fitness based on error, speed, and adaptability."""
        error = self.route_length(self.solution) / 100000
        speed = min(3600 / runtime, 60)
        adapt = min(noise_level / 0.15, 1.5)
        return (1 - error) * speed * adapt
