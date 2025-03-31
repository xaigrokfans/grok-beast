import unittest
from src.scaling import AdaptiveScaler

class TestScaling(unittest.TestCase):
    def setUp(self):
        """Initialize scaler for each test."""
        self.scaler = AdaptiveScaler()

    def test_predict_tribes_small(self):
        """Test tribe prediction for small problem sizes (1.0 baseline)."""
        self.assertEqual(self.scaler.predict_tribes(200), 12)  # k=0.1, z=0.8
        self.assertGreaterEqual(self.scaler.predict_tribes(50), 6)  # Min tribes

    def test_predict_tribes_large(self):
        """Test tribe prediction for large problem sizes (2.0 update)."""
        self.assertGreaterEqual(self.scaler.predict_tribes(5000), 50)  # ~1 tribe/100 items
        self.assertLessEqual(self.scaler.predict_tribes(5000), 60)    # Cap reasonable
        self.assertGreaterEqual(self.scaler.predict_tribes(10000), 70)  # SAT-scale

    def test_tune_low_te(self):
        """Test tuning when tribe efficiency is too low (1.0 baseline)."""
        scaler = AdaptiveScaler()
        scaler.tune(0.01, 100, 439, 0.02, 200)
        self.assertAlmostEqual(scaler.k, 0.08, places=2)  # TE too low → k down

    def test_tune_high_te(self):
        """Test tuning when tribe efficiency is too high (2.0 update)."""
        scaler = AdaptiveScaler()
        scaler.tune(0.05, 100, 5000, 0.02, 1000)
        self.assertAlmostEqual(scaler.k, 0.12, places=2)  # TE too high → k up

    def test_expected_te(self):
        """Test expected tribe efficiency for varying sizes (2.0 update)."""
        self.assertAlmostEqual(self.scaler.expected_te(200), 0.015, places=3)  # 1.0 baseline
        self.assertLess(self.scaler.expected_te(5000), 0.01)  # Larger → lower TE

    def test_expected_ri(self):
        """Test expected route improvement for varying sizes (2.0 update)."""
        self.assertGreaterEqual(self.scaler.expected_ri(439), 150)  # 1.0 baseline
        self.assertGreaterEqual(self.scaler.expected_ri(5000), 500)  # Larger → higher RI

if __name__ == '__main__':
    unittest.main()
