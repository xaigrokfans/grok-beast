import unittest
import time
from src.beast import Beast
from src.harmony import Harmony
from src.main import load_problem

class TestQuantum5000(unittest.TestCase):
    def setUp(self):
        """Initialize test fixtures."""
        self.problem = load_problem("simulations/quantum_5000.qec", "qec")
        self.beast = Beast(domain="qec")
        self.harmony = Harmony(domain="qec")

    def test_load_problem(self):
        """Test QEC problem loading."""
        self.assertEqual(self.problem["qubits"], 5000)
        self.assertEqual(len(self.problem["state"]), 5000)
        self.assertTrue(all(s in [0, 1] for s in self.problem["state"]))

    def test_beast_init(self):
        """Test Beast initialization for QEC."""
        self.assertEqual(self.beast.domain, "qec")
        self.assertIn("parity", self.beast.instincts)
        self.assertEqual(len(self.beast.solution), 0)  # Pre-evolution

    def test_evolve(self):
        """Test Beast evolution for QEC."""
        solution = self.beast.evolve(self.problem, [], [], 0)
        self.assertEqual(len(solution), 5000)  # Matches qubits
        fitness = self.beast.fitness(solution)
        self.assertGreaterEqual(fitness, 0.9)  # ~90% error-free initially (placeholder)

    def test_harmony_fitness(self):
        """Test Harmony fitness for QEC."""
        solution = self.beast.evolve(self.problem, [], [], 0)
        self.harmony.update_cues(self.problem, solution)
        fitness = self.harmony.fitness(solution, self.problem)
        self.assertGreaterEqual(fitness, 0.9)  # Consistent with Beast
        self.assertLessEqual(fitness, 1.0)    # Max 100% error-free

    def test_flow_fitness(self):
        """Test Harmony flow fitness for QEC."""
        start_time = time.time()
        solution = self.beast.evolve(self.problem, [], [], 0)
        runtime = time.time() - start_time
        flow = self.harmony.flow_fitness(solution, self.problem, runtime)
        self.assertGreater(flow, 0)         # Positive flow
        self.assertLess(flow, 100)          # Reasonable cap (speed < 60x)

    def test_noise_resilience(self):
        """Test QEC under 25% noise."""
        noisy_beast = Beast(domain="qec")
        solution = noisy_beast.evolve(self.problem, [], [], 0, noise_level=0.25)
        fitness = noisy_beast.fitness(solution)
        self.assertGreaterEqual(fitness, 0.75)  # ~75% error-free under noise

if __name__ == "__main__":
    unittest.main()
