from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from minesweeper import Game, GamesManager

app = Flask(__name__)
socketio = SocketIO(app)

games_manager = GamesManager()

#~ @socketio.on('socket_connected')
#~ def handle_my_event(message):
    #~ print(message)     

@app.route('/')
def index(): 
    return render_template('index.html')

@socketio.on('start_new_game')
def handle_start_new_game(data):
    difficulty = data['difficulty'].lower()
    game = Game(difficulty) 
    game_id = games_manager.register_game(game)

    response = {
        'game_id': game_id,
        'board': game.board.to_dict(),
    }
    emit('new_game_started', response)
     
@socketio.on('refresh_games_list')
def handle_refresh_games_list():
    response = {
        'games_list': games_manager.get_nonexpired_games(),
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
    getattr(game, move_name)(cell)

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
