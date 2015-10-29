import unittest

from bson.objectid import ObjectId
from pymongo import MongoClient

from models import Game, Player, PlayerTypes

client = MongoClient()
db = client["c4"]
games_collection = db["games"]
players_collection = db["players"]


class TestGame(unittest.TestCase):
    def setUp(self):
        self.dummy_id = ObjectId("dummy_obj_id")
        self.player1_id = Player.new("dummy_player")
        self.player2_id = Player.new("dummy_player")
        self.game_id = Game.new("dummy_game", self.player1_id, "dummy_player")
        Game.set_challenger(self.game_id, self.player2_id)

    def test_get_details_no_game(self):
        game, winner, player_type = Game.get_details(self.dummy_id,
                                                     self.dummy_id)
        self.assertEqual(game, None)
        self.assertEqual(winner, None)
        self.assertEqual(player_type, None)

    def test_make_move(self):
        board = Game.make_move(self.player1_id, self.game_id, 3)
        self.assertEqual(board[5][3], "host")

    def test_make_move_not_turn(self):
        board = Game.make_move(self.player1_id, self.game_id, 3)
        self.assertEqual(board[5][3], "host")
        board = Game.make_move(self.player1_id, self.game_id, 3)
        self.assertEqual(board, [])

    def test_make_move_to_win_player1(self):
        board = Game.make_move(self.player1_id, self.game_id, 3)
        self.assertEqual(board[5][3], "host")
        board = Game.make_move(self.player2_id, self.game_id, 2)
        self.assertEqual(board[5][2], "challenger")
        board = Game.make_move(self.player1_id, self.game_id, 3)
        self.assertEqual(board[4][3], "host")
        board = Game.make_move(self.player2_id, self.game_id, 2)
        self.assertEqual(board[4][2], "challenger")
        board = Game.make_move(self.player1_id, self.game_id, 3)
        self.assertEqual(board[3][3], "host")
        board = Game.make_move(self.player2_id, self.game_id, 2)
        self.assertEqual(board[3][2], "challenger")
        board = Game.make_move(self.player1_id, self.game_id, 3)
        self.assertEqual(board[2][3], "host")

        game, winner, player_type = Game.get_details(self.game_id,
                                                     self.player1_id)
        self.assertEqual(player_type, PlayerTypes.HOST)
        self.assertEqual(winner, "host")

    def test_make_move_to_win_player2(self):
        board = Game.make_move(self.player1_id, self.game_id, 3)
        self.assertEqual(board[5][3], "host")
        board = Game.make_move(self.player2_id, self.game_id, 2)
        self.assertEqual(board[5][2], "challenger")
        board = Game.make_move(self.player1_id, self.game_id, 3)
        self.assertEqual(board[4][3], "host")
        board = Game.make_move(self.player2_id, self.game_id, 2)
        self.assertEqual(board[4][2], "challenger")
        board = Game.make_move(self.player1_id, self.game_id, 3)
        self.assertEqual(board[3][3], "host")
        board = Game.make_move(self.player2_id, self.game_id, 2)
        self.assertEqual(board[3][2], "challenger")
        board = Game.make_move(self.player1_id, self.game_id, 4)
        self.assertEqual(board[5][4], "host")
        board = Game.make_move(self.player2_id, self.game_id, 2)
        self.assertEqual(board[2][2], "challenger")

        game, winner, player_type = Game.get_details(self.game_id,
                                                     self.player2_id)
        self.assertEqual(player_type, PlayerTypes.CHALLENGER)
        self.assertEqual(winner, "challenger")

    def tearDown(self):
        Game.delete(self.game_id)
        Player.delete(self.player1_id)
        Player.delete(self.player2_id)
