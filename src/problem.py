from abc import ABC, abstractmethod
import numpy as np
import random

class Problem(ABC):
    """Base class for problem domains."""
    def __init__(self, domain, data):
        self.domain = domain
        self.data = data

    @abstractmethod
    def initialize_solution(self):
        """Generate an initial solution."""
        pass

    @abstractmethod
    def evaluate_fitness(self, solution):
        """Evaluate the fitness of a solution."""
        pass

    @abstractmethod
    def crossover(self, parent1, parent2):
        """Perform crossover between two solutions."""
        pass

    @abstractmethod
    def mutate(self, solution):
        """Mutate a solution."""
        pass

    def apply_strategy(self, solution, strategy):
        """Apply a specific strategy to the solution (optional)."""
        return solution

    def extract_signals(self, solution):
        """Extract signals from the solution for fractal swaps."""
        return []

    def apply_fractal_swap(self, solution, signals):
        """Apply fractal swap to the solution using provided signals."""
        return solution

    def evaluate_state(self, solution):
        """Evaluate the current state for cultural meme selection (optional)."""
        return {}

class TSPProblem(Problem):
    """Problem subclass for the Traveling Salesman Problem (TSP)."""
    def __init__(self, data):
        super().__init__('tsp', data)
        self.coords = np.array(data)
        self.dist_matrix = np.sqrt(
            (self.coords[:, 0, None] - self.coords[:, 0])**2 +
            (self.coords[:, 1, None] - self.coords[:, 1])**2
        )

    def initialize_solution(self):
        n_cities = len(self.data)
        solution = list(range(n_cities))
        random.shuffle(solution)
        return solution

    def evaluate_fitness(self, solution):
        indices = np.array(solution)
        distance = np.sum(self.dist_matrix[indices[:-1], indices[1:]]) + \
                   self.dist_matrix[indices[-1], indices[0]]
        return -distance  # Negative because we minimize distance

    def crossover(self, parent1, parent2):
        # Ordered crossover (OX)
        size = len(parent1)
        start, end = sorted(random.sample(range(size), 2))
        child = [None] * size
        child[start:end] = parent1[start:end]
        remaining = [x for x in parent2 if x not in child[start:end]]
        j = 0
        for i in range(size):
            if child[i] is None:
                child[i] = remaining[j]
                j += 1
        return child

    def mutate(self, solution):
        # Swap mutation
        i, j = random.sample(range(len(solution)), 2)
        solution[i], solution[j] = solution[j], solution[i]
        return solution

    def apply_strategy(self, solution, strategy):
        if strategy == '2-opt':
            return self.two_opt(solution)
        return solution

    def two_opt(self, solution):
        best = solution[:]
        improved = True
        while improved:
            improved = False
            for i in range(1, len(best) - 2):
                for j in range(i + 2, len(best)):
                    if j - i == 1:
                        continue
                    delta = (self.dist_matrix[best[i-1], best[j-1]] + self.dist_matrix[best[i], best[j]]) - \
                            (self.dist_matrix[best[i-1], best[i]] + self.dist_matrix[best[j-1], best[j]])
                    if delta < 0:
                        best[i:j] = best[i:j][::-1]
                        improved = True
            break  # Single pass for efficiency
        return best

    def extract_signals(self, solution):
        chunk_size = 10
        segments = [solution[i:i + chunk_size] for i in range(0, len(solution) - chunk_size + 1, chunk_size)]
        signals = []
        for seg in segments:
            fitness = self.evaluate_fitness(seg + [seg[0]])  # Close the loop for segment
            signals.append((seg, fitness, 0))  # Epigenetic tag placeholder
        return signals

    def apply_fractal_swap(self, solution, signals):
        depth = min(5, len(solution) // 10)
        chunk_size = max(1, len(solution) // depth)
        solution_set = set(solution)
        for i in range(0, len(solution), chunk_size):
            chunk = solution[i:i + chunk_size]
            best_signal = max(signals, key=lambda s: s[1], default=(chunk, 0, 0))
            signal_seg = best_signal[0]
            if len(signal_seg) == len(chunk) and set(signal_seg).issubset(solution_set):
                if self.evaluate_fitness(signal_seg + [signal_seg[0]]) > self.evaluate_fitness(chunk + [chunk[0]]):
                    solution[i:i + chunk_size] = signal_seg
        return solution

    def evaluate_state(self, solution):
        fitness = self.evaluate_fitness(solution)
        return {'fitness': fitness, 'length': len(solution)}
