import unittest

class ExampleTestSuite(unittest.TestCase):
    def example_test(self):
        res = 2 + 2
        self.assertEqual(4, res)
