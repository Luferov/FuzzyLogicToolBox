import unittest
from fuzzy_logic.mf import TriangularMF


class FuzzyVariablesTestCase(unittest.TestCase):

    def setUp(self) -> None:
        print(f'setUp: {self.__class__.__name__}\n')
        self.tmf: TriangularMF = TriangularMF(0, 0.5, 1)

    def tearDown(self) -> None:
        print(f'tearDown: {self.__class__.__name__}\n')

    def test_triangular_value(self):

        self.assertEqual(self.tmf.get_value(0.5), 1)
        self.assertEqual(self.tmf.get_value(0), 0)
        self.assertEqual(self.tmf.get_value(0.25), 0.5)
        self.assertEqual(self.tmf.get_value(1), 0)
        self.assertEqual(self.tmf.get_value(0.75), 0.5)


if __name__ == '__main__':
    unittest.main()
