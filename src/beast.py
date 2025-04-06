class Beast:
    """Represents an individual in the population."""
    def __init__(self, problem, role='local', tribe_id=0):
        self.problem = problem
        self.role = role
        self.tribe_id = tribe_id
        self.solution = problem.initialize_solution()

    def fitness(self):
        """Evaluate the fitness of the current solution."""
        return self.problem.evaluate_fitness(self.solution)
