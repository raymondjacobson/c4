import unittest

from models import Board


class TestGame(unittest.TestCase):
    def test_horizontal_victory(self):
        b = Board.new()
        b[len(b) - 1][0] = 1
        b[len(b) - 1][1] = 1
        b[len(b) - 1][2] = 1
        b[len(b) - 1][3] = 1
        self.assertEqual(Board.score(b), 1)

    def test_no_horizontal_victory(self):
        b = Board.new()
        b[len(b) - 1][0] = 1
        b[len(b) - 1][1] = 1
        b[len(b) - 1][2] = 0
        b[len(b) - 1][3] = 1
        self.assertEqual(Board.score(b), 0)

    def test_vertical_victory(self):
        b = Board.new()
        b[len(b) - 1][0] = 1
        b[len(b) - 2][0] = 1
        b[len(b) - 3][0] = 1
        b[len(b) - 4][0] = 1
        self.assertEqual(Board.score(b), 1)

    def test_no_vertical_victory(self):
        b = Board.new()
        b[len(b) - 1][0] = 1
        b[len(b) - 2][0] = 0
        b[len(b) - 3][0] = 1
        b[len(b) - 4][0] = 1
        self.assertEqual(Board.score(b), 0)

    def test_diagonal_right_victory(self):
        b = Board.new()
        b[len(b) - 1][0] = 1
        b[len(b) - 2][1] = 1
        b[len(b) - 3][2] = 1
        b[len(b) - 4][3] = 1
        self.assertEqual(Board.score(b), 1)

    def test_diagonal_left_victory(self):
        b = Board.new()
        b[len(b) - 4][0] = 1
        b[len(b) - 3][1] = 1
        b[len(b) - 2][2] = 1
        b[len(b) - 1][3] = 1
        self.assertEqual(Board.score(b), 1)

    def test_no_diagonal_victory(self):
        b = Board.new()
        b[len(b) - 1][0] = 1
        b[len(b) - 2][1] = 1
        b[len(b) - 3][2] = 1
        b[len(b) - 4][2] = 1
        self.assertEqual(Board.score(b), 0)

if __name__ == '__main__':
    unittest.main()
