import unittest
from dataclasses import dataclass

from src.utils.dataset import index_by


@dataclass
class TestClass:
    x: int
    y: str


class MyTestCase(unittest.TestCase):
    def test_index_by(self):
        data_set = [TestClass(1, "a"), TestClass(2, "b"), TestClass(3, "b")]
        expected = {
            1: data_set[0],
            2: data_set[1],
            3: data_set[2]
        }
        self.assertEqual(index_by(data_set, 'x'), expected)

        with self.assertRaises(IndexError):
            index_by(data_set, 'y')

        with self.assertRaises(AssertionError):
            index_by(data_set, 'non-existent field')


if __name__ == '__main__':
    unittest.main()
