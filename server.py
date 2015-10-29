from flask import Flask, jsonify, redirect, render_template, request, session, \
    url_for
from flask.ext.session import Session

from middleware import ReverseProxied
from models import Game, Player

app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.debug = True
SESSION_TYPE = 'redis'
app.config.from_object(__name__)
Session(app)


@app.route("/", methods=['GET'])
def index():
    # Check if the visitor is a current valid user
    if '_id' in session.keys() and Player.load(session['_id']):
        player = Player.load(session['_id'])
        games = list(Game.get_games())
        return render_template('index.html',
                               title="C4 4 PG",
                               games=games,
                               player=player)
    else:
        return render_template('new_player.html',
                               title="C4 4 PG | new player",
                               destination=url_for('index'))


@app.route("/admin", methods=['POST'])
def admin():
    p_id = Player.new(request.form['name'])
    session['_id'] = p_id
    return redirect(request.form['destination'])


@app.route("/game/new", methods=['POST'])
def new_game():
    player = Player.load(session['_id'])
    game_id = Game.new(request.form['name'], player['_id'], player['name'])
    return redirect("game/" + str(game_id))


@app.route("/game/<game_id>", methods=['GET'])
def get_game(game_id):
    if '_id' in session.keys() and Player.load(session['_id']):
        player_id = session['_id']
        player = Player.load(player_id)
        game, winner, player_type = Game.get_details(game_id, player_id)
        if not game:
            return redirect(url_for('index'))
        return render_template('game.html',
                               title="C4 4 PG | " + game_id,
                               game=game,
                               player=player,
                               winner=winner,
                               player_type=player_type)
    else:
        return render_template('new_player.html',
                               title="C4 4 PG | new player",
                               destination=url_for('get_game',
                                                   game_id=game_id))


@app.route("/game/<game_id>", methods=['DELETE'])
def delete_game(game_id):
    if 'two_player_confirm_delete' not in request.form.keys():
        Game.delete(game_id)
        return 'Game drop'
    Game.delete_if_both_players_confirm(game_id)
    return 'Two player game drop'


@app.route("/game/<game_id>/board", methods=['GET'])
def load_board(game_id):
    game = Game.get(game_id)
    if not game:
        return jsonify(active=False)
    winner = Game.score(game_id)
    host_turn = game['host_turn']
    host_name = game['host_name']
    board = game['board']
    if 'challenger' in game.keys():
        challenger_name = Player.load(game['challenger'])['name']
    else:
        challenger_name = "Waiting for a challenger"
    return jsonify(active=True,
                   board=board,
                   winner=winner,
                   host_turn=host_turn,
                   host_name=host_name,
                   challenger_name=challenger_name)


@app.route("/move", methods=['POST'])
def move():
    player_id = session['_id']
    game_id = request.form['game_id']
    move_location = request.form['move_location']

    Game.make_move(player_id, game_id, move_location)

    return redirect("game/" + str(game_id))

if __name__ == "__main__":
    app.run()
