import datetime
from bson.objectid import ObjectId
from pymongo import MongoClient

from enum import enum

client = MongoClient()
db = client["c4"]
games_collection = db["games"]
players_collection = db["players"]


PlayerTypes = enum(SPECTATOR='spectator', HOST='host', CHALLENGER='challenger')


class Game():
    '''
    This class wraps the MongoDB game collection
    Schema:
      - name
      - host_id
      - host_name
      - board
      - host_turn
      - last_access
      - challenger
      - staged_delete (used to confirm a game delete from both players when
                       a game ends)
    '''
    @classmethod
    def new(cls, name, host_id, host_name):
        if name == "":
            name = host_name + "'s game"
        _id = games_collection.insert_one({
            "name": name,
            "host_id": host_id,
            "host_name": host_name,
            "board": Board.new(),
            "host_turn": True,
            "last_access": datetime.datetime.utcnow()
        }).inserted_id
        return _id

    @classmethod
    def get(cls, _id):
        return games_collection.find_one({"_id": ObjectId(_id)})

    @classmethod
    def get_details(cls, game_id, player_id):
        game = Game.get(game_id)
        if not game:
            return None, None, None
        winner = Game.score(game_id)
        player_type = PlayerTypes.HOST
        if game['host_id'] != player_id:
            player_type = PlayerTypes.CHALLENGER
            # The first visitor to the game is the challenger
            if 'challenger' not in game.keys():
                Game.set_challenger(game_id, player_id)
                game = Game.get(game_id)
            if game['challenger'] != player_id:
                player_type = PlayerTypes.SPECTATOR
        return game, winner, player_type

    @classmethod
    def delete(cls, _id):
        games_collection.delete_one({"_id": ObjectId(_id)})

    @classmethod
    def delete_if_both_players_confirm(cls, _id):
        # Stage the game for a delete, but wait for confirmation
        # from both players to actually delete it
        game = cls.get(_id)
        if "staged_delete" in game.keys():
            games_collection.delete_one({"_id": ObjectId(_id)})
        else:
            games_collection.update_one({"_id": ObjectId(_id)},
                                        {"$set": {"staged_delete": True}})

    @classmethod
    def get_games(cls):
        return games_collection.find()

    @classmethod
    def set_challenger(cls, _id, challenger):
        games_collection.update_one({"_id": ObjectId(_id)},
                                    {"$set": {"challenger": challenger}})

    @classmethod
    def set_board(cls, _id, board, host_turn):
        games_collection.update_one({"_id": ObjectId(_id)},
                                    {"$set": {"board": board,
                                              "host_turn": not host_turn,
                                              "last_access":
                                              datetime.datetime.utcnow()}})

    @classmethod
    def score(cls, _id):
        game = games_collection.find_one({"_id": ObjectId(_id)})
        if game:
            board = game["board"]
            return Board.score(board)
        return 0

    @classmethod
    def make_move(cls, player_id, game_id, move_location):
        game = Game.get(game_id)
        board = game['board']
        new_board = []
        # Check which player to place the token for and check
        # that the player has the current board move
        if game['host_id'] == player_id and game['host_turn']:
            new_board = Board.update(board, move_location, PlayerTypes.HOST)
            Game.set_board(game_id, new_board, True)
        elif 'challenger' in game.keys() and \
             game['challenger'] == player_id and not game['host_turn']:

            new_board = Board.update(board, move_location,
                                     PlayerTypes.CHALLENGER)
            Game.set_board(game_id, new_board, False)
        return new_board


class Board():
    '''
    This class wraps a board, stored as a 6x7 array
    '''
    @classmethod
    def new(cls):
        return [[0 for x in xrange(7)] for y in xrange(6)]

    @classmethod
    def update(cls, state, column, pid):
        column = int(column)
        for r in xrange(len(state) - 1, -1, -1):
            if state[r][column] == 0:
                state[r][column] = pid
                break
        return state

    @classmethod
    def score_rows(cls, state):
        for row in xrange(len(state)):
            for col in xrange(3, len(state[row])):
                if 0 != state[row][col - 3] == state[row][col - 2] == \
                   state[row][col - 1] == state[row][col]:
                    return state[row][col]
        return 0

    @classmethod
    def score_columns(cls, state):
        for col in xrange(len(state[0])):
            for row in xrange(3, len(state)):
                if 0 != state[row - 3][col] == state[row - 2][col] == \
                   state[row - 1][col] == state[row][col]:
                    return state[row][col]
        return 0

    @classmethod
    def score_diagonals(cls, state):
        for row in xrange(len(state) - 4, -1, -1):
            for col in xrange(3, len(state[row])):
                if 0 != state[row + 3][col - 3] == state[row + 2][col - 2] == \
                   state[row + 1][col - 1] == state[row][col]:
                    return state[row][col]
                if 0 != state[row + 3][col] == state[row + 2][col - 1] == \
                   state[row + 1][col - 2] == state[row][col - 3]:
                    return state[row + 3][col]
        return 0

    @classmethod
    def score(cls, state):
        return cls.score_rows(state) or cls.score_columns(state) or \
            cls.score_diagonals(state)


class Player():
    '''
    This class wraps the MongoDB player object
    Maintains a name and unique ID
    '''
    @classmethod
    def new(cls, name):
        _id = players_collection.insert_one({"name": name}).inserted_id
        return _id

    @classmethod
    def delete(cls, _id):
        return players_collection.delete_one({"_id": ObjectId(_id)})

    @classmethod
    def load(cls, _id):
        return players_collection.find_one({"_id": ObjectId(_id)})
