import unittest
import time
from src.beast import Beast
from src.harmony import Harmony
from src.main import load_problem

class TestProtein100(unittest.TestCase):
    def setUp(self):
        """Initialize test fixtures."""
        self.problem = load_problem("simulations/protein_100.fasta", "fold")
        self.beast = Beast(domain="fold")
        self.harmony = Harmony(domain="fold")

    def test_load_problem(self):
        """Test protein problem loading."""
        self.assertEqual(len(self.problem["sequence"]), 100)
        self.assertEqual(len(self.problem["angles"]), 200)  # 2 angles per residue (phi/psi)
        self.assertTrue(all(isinstance(a, float) for a in self.problem["angles"]))

    def test_beast_init(self):
        """Test Beast initialization for folding."""
        self.assertEqual(self.beast.domain, "fold")
        self.assertIn("helix", self.beast.instincts)
        self.assertEqual(len(self.beast.solution), 0)  # Pre-evolution

    def test_evolve(self):
        """Test Beast evolution for folding."""
        solution = self.beast.evolve(self.problem, [], [], 0)
        self.assertEqual(len(solution), 200)  # 100 residues * 2 angles
        fitness = self.beast.fitness(solution)
        self.assertGreaterEqual(fitness, 0.7)  # ~0.7+ TM-score (placeholder)

    def test_harmony_fitness(self):
        """Test Harmony fitness for folding."""
        solution = self.beast.evolve(self.problem, [], [], 0)
        self.harmony.update_cues(self.problem, solution)
        fitness = self.harmony.fitness(solution, self.problem)
        self.assertGreaterEqual(fitness, 0.7)  # Consistent with Beast
        self.assertLessEqual(fitness, 1.0)    # Max TM-score 1.0

    def test_flow_fitness(self):
        """Test Harmony flow fitness for folding."""
        start_time = time.time()
        solution = self.beast.evolve(self.problem, [], [], 0)
        runtime = time.time() - start_time
        flow = self.harmony.flow_fitness(solution, self.problem, runtime)
        self.assertGreater(flow, 0)         # Positive flow
        self.assertLess(flow, 100)          # Reasonable cap (speed < 60x)

    def test_noise_resilience(self):
        """Test folding under 25% noise."""
        noisy_beast = Beast(domain="fold")
        solution = noisy_beast.evolve(self.problem, [], [], 0, noise_level=0.25)
        fitness = noisy_beast.fitness(solution)
        self.assertGreaterEqual(fitness, 0.65)  # ~0.65+ TM-score under noise

if __name__ == "__main__":
    unittest.main()
