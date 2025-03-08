# tests/test_pr439.py
import unittest
from src.main import load_tsp, main

class TestPR439(unittest.TestCase):
    def test_load(self):
        cities = load_tsp("../simulations/pr439.tsp")
        self.assertEqual(len(cities), 439)

    def test_run(self):
        # Simplified—real test needs mock LKH
        main("../simulations/pr439.tsp")  # Check output manually

if __name__ == '__main__':
    unittest.main()
