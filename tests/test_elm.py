import unittest
from src.beast import Beast
from src.elm import ELM

def test_elm_integration(self):
    elm = ELM("tsp")
    elm.evolve([self.beast], 0)
    self.assertTrue(len(elm.rules) > 0)

class TestELM(unittest.TestCase):
    def setUp(self):
        """Initialize test fixtures."""
        # Dummy TSP problem: 10 cities
        self.problem = [(i, i) for i in range(10)]
        self.beast = Beast(domain="tsp")

    def test_elm_rule_generation(self):
        """Test ELM rule generation."""
        rule = self.beast.generate_elm_rule(self.problem, gen=5)
        self.assertIn("condition", rule)
        self.assertIn("actions", rule)
        self.assertTrue(any(c in rule["condition"] for c in ["noise", "gen"]))  # Valid condition
        self.assertIn(rule["actions"][0], ["4-opt", "core swaps"])  # TSP actions

    def test_check_condition(self):
        """Test ELM condition evaluation."""
        rule = {"condition": "noise > 0.2", "actions": ["4-opt"]}
        self.assertTrue(self.beast.check_condition(rule["condition"], self.problem, 0, 0.25))
        self.assertFalse(self.beast.check_condition(rule["condition"], self.problem, 0, 0.1))
        rule = {"condition": "gen > 10", "actions": ["4-opt"]}
        self.assertTrue(self.beast.check_condition(rule["condition"], self.problem, 15, 0))
        self.assertFalse(self.beast.check_condition(rule["condition"], self.problem, 5, 0))

    def test_execute_action(self):
        """Test ELM action execution."""
        self.beast.solution = self.beast.nearest_neighbor(self.problem[:])
        initial_length = self.beast.route_length(self.beast.solution)
        self.beast.execute_action(["4-opt"], self.problem)
        new_length = self.beast.route_length(self.beast.solution)
        self.assertLessEqual(new_length, initial_length)  # 4-opt should improve or maintain

    def test_apply_elm_rules(self):
        """Test applying ELM rules during evolution."""
        self.beast.elm_rules = [{"condition": "noise > 0.1", "actions": ["4-opt"]}]
        solution = self.beast.evolve(self.problem, [], [], 0, noise_level=0.25)
        self.assertTrue(len(solution) == len(self.problem))  # Valid route
        fitness = self.beast.fitness(solution)
        self.assertLess(fitness, 0)  # Negative length (TSP fitness)

    def test_rule_mutation(self):
        """Test ELM rule mutation during evolution."""
        initial_rules = len(self.beast.elm_rules)
        for _ in range(10):  # Run multiple evolutions to trigger mutation (~10% chance)
            self.beast.evolve(self.problem, [], [], 0)
        self.assertGreater(len(self.beast.elm_rules), initial_rules)  # Mutation adds rules

    def test_noise_resilience(self):
        """Test ELM under noise."""
        self.beast.elm_rules = [{"condition": "noise > 0.2", "actions": ["4-opt"]}]
        solution = self.beast.evolve(self.problem, [], [], 0, noise_level=0.25)
        fitness_noisy = self.beast.fitness(solution)
        solution_clean = self.beast.evolve(self.problem, [], [], 0, noise_level=0)
        fitness_clean = self.beast.fitness(solution_clean)
        self.assertGreaterEqual(fitness_noisy, fitness_clean * 0.9)  # ~90% of clean fitness

if __name__ == "__main__":
    unittest.main()
