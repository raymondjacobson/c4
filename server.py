from flask import Flask, jsonify, redirect, render_template, request, session, \
    url_for
from flask.ext.session import Session

from middleware import ReverseProxied
from models import Board, Game, Player, PlayerTypes

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


@app.route('/game/<game_id>/delete', methods=['POST'])
def delete_game(game_id):
    Game.drop(game_id)
    return redirect(url_for('index'))


@app.route('/game/<game_id>/joint_delete', methods=['POST'])
def joint_delete_game(game_id):
    Game.staged_drop(game_id)
    return redirect(url_for('index'))


@app.route("/game/<game_id>", methods=['GET'])
def view_game(game_id):
    if '_id' in session.keys() and Player.load(session['_id']):
        player = Player.load(session['_id'])
        game = Game.get(game_id)
        if not game:
            return redirect(url_for('index'))
        winner = Game.score(game_id)
        player_type = PlayerTypes.HOST
        if game['host_id'] != player['_id']:
            player_type = PlayerTypes.CHALLENGER
            # The first visitor to the game is the challenger
            if 'challenger' not in game.keys():
                Game.set_challenger(game_id, player['_id'])
                game = Game.get(game_id)
            # Render a tempalate for a spectator if they're
            # not either of the players
            if game['challenger'] != player['_id']:
                player_type = PlayerTypes.SPECTATOR
        return render_template('game.html',
                               title="C4 4 PG | " + game_id,
                               game=game,
                               player=player,
                               winner=winner,
                               player_type=player_type)
    else:
        return render_template('new_player.html',
                               title="C4 4 PG | new player",
                               destination=url_for('view_game',
                                                   game_id=game_id))


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
    p = Player.load(session['_id'])
    game_id = request.form['game_id']
    move_location = request.form['move_location']

    # Get the current board and update it with the new move
    game = Game.get(game_id)
    board = game['board']
    # Check which player to place the token for and check
    # that the player has the current board move
    if game['host_id'] == p['_id'] and game['host_turn']:
        new_board = Board.update(board, move_location, PlayerTypes.HOST)
        Game.set_board(game_id, new_board, True)
    elif 'challenger' in game.keys() and \
         game['challenger'] == p['_id'] and not game['host_turn']:

        new_board = Board.update(board, move_location, PlayerTypes.CHALLENGER)
        Game.set_board(game_id, new_board, False)

    return redirect("game/" + str(game_id))

if __name__ == "__main__":
    app.run()
