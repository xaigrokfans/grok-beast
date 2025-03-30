import unittest
import time
from src.beast import Beast
from src.harmony import Harmony
from src.main import load_problem

class TestSAT10000(unittest.TestCase):
    def setUp(self):
        """Initialize test fixtures."""
        self.problem = load_problem("simulations/sat_10000.cnf", "sat")
        self.beast = Beast(domain="sat")
        self.harmony = Harmony(domain="sat")

    def test_load_problem(self):
        """Test SAT problem loading."""
        self.assertEqual(self.problem["vars"], 10000)
        self.assertTrue(len(self.problem["clauses"]) > 0)
        self.assertIsInstance(self.problem["clauses"][0], tuple)

    def test_beast_init(self):
        """Test Beast initialization for SAT."""
        self.assertEqual(self.beast.domain, "sat")
        self.assertIn("flip", self.beast.instincts)
        self.assertEqual(len(self.beast.solution), 0)  # Pre-evolution

    def test_evolve(self):
        """Test Beast evolution for SAT."""
        solution = self.beast.evolve(self.problem, [], [], 0)
        self.assertEqual(len(solution), 10000)  # Matches vars
        fitness = self.beast.fitness(solution)
        self.assertGreaterEqual(fitness, 0.5)  # ~50% clauses satisfied initially

    def test_harmony_fitness(self):
        """Test Harmony fitness for SAT."""
        solution = self.beast.evolve(self.problem, [], [], 0)
        self.harmony.update_cues(self.problem, solution)
        fitness = self.harmony.fitness(solution, self.problem)
        self.assertGreaterEqual(fitness, 0.5)  # Consistent with Beast
        self.assertLessEqual(fitness, 1.0)    # Max 100% satisfaction

    def test_flow_fitness(self):
        """Test Harmony flow fitness for SAT."""
        start_time = time.time()
        solution = self.beast.evolve(self.problem, [], [], 0)
        runtime = time.time() - start_time
        flow = self.harmony.flow_fitness(solution, self.problem, runtime)
        self.assertGreater(flow, 0)         # Positive flow
        self.assertLess(flow, 100)          # Reasonable cap (speed < 60x)

    def test_noise_resilience(self):
        """Test SAT solving under noise."""
        noisy_beast = Beast(domain="sat")
        solution = noisy_beast.evolve(self.problem, [], [], 0, noise_level=0.25)
        fitness = noisy_beast.fitness(solution)
        self.assertGreaterEqual(fitness, 0.4)  # ~40% under 25% noise

if __name__ == "__main__":
    unittest.main()
