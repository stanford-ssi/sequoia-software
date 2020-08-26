import unittest
from Examples.UnitTesting.sampleClass import ObjectCreator


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.sampleObject = ObjectCreator("Test")

    def tearDown(self) -> None:
        pass

    def test_setter(self) -> None:
        test_value = "xzy"
        self.sampleObject.set_value(test_value)
        self.assertEqual(test_value, self.sampleObject.get_value())

    def test_random_generator(self) -> None:
        mins = [-1, 5, 9, 4]
        max = [100, 40, 20, 14]
        lengths = [4, 2, 56, 3]

        for i in range(len(mins)):
            res = self.sampleObject.get_random_numbers(mins[i], max[i], lengths[i])
            self.assertEqual(len(res), lengths[i])
            for result in res:
                self.assertGreaterEqual(result, mins[i])
                self.assertLessEqual(result, max[i])

    def test_break_order(self) -> None:
        self.assertRaises(ValueError, self.sampleObject.get_random_numbers, 10, 4, 10)

    def test_break_length(self) -> None:
        res = self.sampleObject.get_random_numbers(1, 10, -3)
        self.assertEqual(res, [])


if __name__ == '__main__':
    unittest.main()
