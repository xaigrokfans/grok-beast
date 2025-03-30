# tests/test_scaling.py
import unittest
from src.scaling import AdaptiveScaler

class TestScaling(unittest.TestCase):
    def test_predict(self):
        scaler = AdaptiveScaler()
        self.assertEqual(scaler.predict_tribes(200), 12)  # k=0.1, z=0.8
        self.assertGreaterEqual(scaler.predict_tribes(50), 6)  # Min tribes

    def test_tune(self):
        scaler = AdaptiveScaler()
        scaler.tune(0.01, 100, 439, 0.02, 200)
        self.assertAlmostEqual(scaler.k, 0.08, places=2)  # TE too low → k down

if __name__ == '__main__':
    unittest.main()
