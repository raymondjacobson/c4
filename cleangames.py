# please rename this file "clean_games.py"
import datetime
from bson.objectid import ObjectId 
from pymongo import MongoClient

client = MongoClient()
db = client['c4']
games_collection = db['games']

def clean(minutes_delta):
  """
  This method is a helper that cleans out all existing games in the database
  that haven't been touched for minutes_delta time.
  """
  for game in games_collection.find():
    if datetime.datetime.utcnow() - game['last_access'] > datetime.timedelta(minutes=delta):
      games_collection.delete_one({"_id": game['_id']})

if __name__ == '__main__':
  clean(10)