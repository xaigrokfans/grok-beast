# tests/test_pr1002.py
import unittest
from src.main import load_tsp

class TestPR1002(unittest.TestCase):
    def test_load(self):
        cities = load_tsp("../simulations/pr1002.tsp")
        self.assertEqual(len(cities), 1002)

if __name__ == '__main__':
    unittest.main()
