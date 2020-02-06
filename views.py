import uuid
import datetime
import os

from flask import (
    Flask, 
    render_template, 
    Response, 
    jsonify,
    request,
    session,
)
from flask_socketio import SocketIO, emit

from minesweeper import Game, GamesManager

games_manager = GamesManager()

app = Flask(__name__)
socketio = SocketIO(app)
	
@app.route('/')
def index(): 
    return render_template('index.html')

@socketio.on('my event')
def handle_my_event(message):
	print(message)

@socketio.on('start_new_game')
def handle_start_new_game():
    game = Game()   
    game_id = games_manager.register_game(game)

    response = {
        'game_id': game_id,
        'board': game.board.to_dict(),
        'games_list': [g for g in games_manager.games.keys()]
    }
    emit('new_game_started', response)
    
@socketio.on('refresh_games_list')
def handle_refresh_games_list():
	games_list = [
        {
            'id': k,
            'started_ago': round((datetime.datetime.now() - games_manager.games[k]['game_creation_date']).total_seconds() / 60),
            'completion': str(games_manager.games[k]['game'].completion()),
        }
        for k, v in games_manager.games.items()
    ] 
	response = {
		'games_list': games_list,
	}
	emit('games_list_refreshed', response, broadcast=True)
    
@socketio.on('board_move')
def handle_board_move(data):
	game_id = data['game_id']
	game = games_manager.get_game(game_id)

	row = int(data['row'])
	col = int(data['col'])
	cell = game.board[row][col]

	move_name = data['move_name']
	if move_name == 'reveal_cell_area':
		game.reveal_cell_area(cell)       
	if move_name == 'toggle_flag':
		game.toggle_flag(row, col)

	if game.end_status:
		games_manager.unregister_game(game_id)
		
	response = {
		'game_id': game_id,
		'board': game.board.to_dict(),
		'end_status': game.end_status,
	}
	emit('board_changed', response, broadcast=True)
	
@socketio.on('switch_game')
def handle_switch_game(data):
	game_id = data['game_id']
	game = games_manager.get_game(game_id)
	response = {
		'game_id': game_id,
		'board': game.board.to_dict(),
	}
	emit('game_switched', response)
	
if __name__ == '__main__':
	socketio.run(app, port=8000)
    #~ app.run(port=8000)
    # app.run(host='192.168.1.14', port=5010)
