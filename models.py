# Please install a python linter and apply it to all the code
# (will only take a few minutes).
# Note that as you do so, please keep such formatting changes
# in their own git commit. Avoid mixing semantic changes with
# style changes, otherwise it becomes hard to tell what's really
# changing.
import datetime
from bson.objectid import ObjectId 
from pymongo import MongoClient

client = MongoClient()
db = client['c4']
games_collection = db['games']
players_collection = db['players']

# This kind of utility, although small, is very general-use and
# would be more cleanly placed in its own module.
def enum(**enums):
    return type('Enum', (), enums)

PlayerTypes = enum(SPECTATOR='spectator', HOST='host', CHALLENGER='challenger')

class Game():
  """
  This class wraps the MongoDB game object
  # In this case, "collection" is a more precise word than "object".
  # This may seem like a tiny nit, but naming things precisely is important
  # for readability. Every small hesitation due to ambiguity that we
  # introduce into the code-reading experience adds up to harder-to-maintain
  # code.
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
  """
  @classmethod
  # Why all these class methods rather than just instance methods?
  def new(self, name, host_id, host_name):
  # E.g., why isn't this just a regular python constructor?
  # Unless there's a really strong reason, it seems more intuitive to use class
  # instances the normal way.
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
  def get(self, _id):
    return games_collection.find_one({"_id": ObjectId(_id)})

  @classmethod
  def drop(self, _id):
    games_collection.delete_one({"_id": ObjectId(_id)})

  @classmethod
  def staged_drop(self, _id):
    # "Staged" doesn't really call any image to mind unless I read the comment
    # to understand your special meaning.
    # How about calling this something more self-describing like
    # "delete_if_both_players_confirm"?

    # Stage the game for a drop, but wait for confirmation from both players
    # to actually drop it
    game = self.get(_id)
    if 'staged_delete' in game.keys():
    # Please stay consistent with your quotes (single vs double).
    # Match the prevailing convention established by the surrounding file,
    # avoid random variations as a general rule, to aid readability.
      games_collection.delete_one({"_id": ObjectId(_id)})
    else:
      games_collection.update_one({"_id": ObjectId(_id)},
                                  {"$set": {"staged_delete": True} })

  @classmethod
  def get_games(self):
    return games_collection.find()

  @classmethod
  def set_challenger(self, _id, challenger):
    games_collection.update_one({"_id": ObjectId(_id)},
                                {"$set": {"challenger": challenger} })

  @classmethod
  def set_board(self, _id, board, host_turn):
    games_collection.update_one({"_id": ObjectId(_id)},
                                {"$set": {"board": board,
                                          "host_turn": not host_turn,
                                          "last_access": datetime.datetime.utcnow()} })

  @classmethod
  def score(self, _id):
    game = games_collection.find_one({"_id": ObjectId(_id)})
    if game:
      board = game['board']
      return Board.score(board)
    return 0


class Board():
  """
  This class wraps the MongoDB board object, stored as a 6x7 array
  """
  @classmethod
  def new(self):
    return [ [0 for x in xrange(7)] for y in xrange(6) ]

  @classmethod
  def update(self, state, column, pid):
    column = int(column)
    for r in xrange(len(state)-1, -1, -1):
      if state[r][column] == 0:
        state[r][column] = pid
        break
    return state

  @classmethod
  def score(self, state):
    # Please delete these 3 comments and replace them with functions named in
    # a self-describing way, e.g., "score_rows". This serves ~5 purposes:
    # (1) It lets the code itself "tell a story" about what it does, which
    # is a direct aid to readability.
    # (2) It avoids reliance on comments which can and do fall out of sync
    # with reality.
    # (3) It keeps each function single-purpose.
    # (4) It keeps each function shorter and therefore easier to read.
    # (5) It makes tests also single-purpose and shorter.

    # Score the rows
    for row in xrange(len(state)):
      for col in xrange(3, len(state[row])):
        if 0 != state[row][col-3] == state[row][col-2] == state[row][col-1] == state[row][col]:
          return state[row][col]

    # Score the columns
    for col in xrange(len(state[0])):
      for row in xrange(3, len(state)):
        if 0 != state[row-3][col] == state[row-2][col] == state[row-1][col] == state[row][col]:
          return state[row][col]

    # Score the diagonals
    for row in xrange(len(state)-4, -1, -1):
      for col in xrange(3, len(state[row])):
        if 0 != state[row+3][col-3] == state[row+2][col-2] == state[row+1][col-1] == state[row][col]:
          return state[row][col]
        if 0 != state[row+3][col] == state[row+2][col-1] == state[row+1][col-2] == state[row][col-3]:
          return state[row+3][col]
    return 0

class Player():
  """
  This class wraps the MongoDB player object
  Maintains a name and unique ID
  """
  @classmethod
  def new(self, name):
    _id = players_collection.insert_one({"name":name}).inserted_id
    return _id

  @classmethod
  def load(self, _id):
    return players_collection.find_one({"_id":ObjectId(_id)})
