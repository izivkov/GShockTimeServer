# filepath: gshock_api/tests/test_core.py
import unittest
from gshock_api import core

class TestCore(unittest.TestCase):
    def test_example_function(self):
        self.assertEqual(core.example_function(), "Hello from gshock_api core!")

if __name__ == '__main__':
    unittest.main()
    