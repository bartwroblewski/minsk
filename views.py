import uuid
import datetime

from flask import (
    Flask, 
    render_template, 
    Response, 
    jsonify,
    request,
    url_for
)
from minesweeper import Game, GameManager

app = Flask(__name__)
game_manager = GameManager()

@app.route('/')
def index(): 
	print(url_for('get_game_board', _external=True))
	return render_template('index.html')

@app.route('/start_new_game')
def start_new_game():
    game_id = str(uuid.uuid4())
    game = Game(id_=game_id)
    
    game_manager.register_game(game)
    game_manager.unregister_old_games()
    
    print('CURRENT GAMES', len(game_manager.games))
    
    response = {
        'current_games_ids': [
            game_id 
            for game_id, game in sorted(game_manager.games.items()) 
        ],
        'game_id': game.id_,
        'board': game.board.to_dict(),
    }
    return jsonify(response)
    
@app.route('/get_game_board')
def get_game_board():
    game_id = request.args.get('game_id')
    game = game_manager.get_game(game_id)
    
    response = {
        'board': game.board.to_dict(),
    }
    return jsonify(response)
    
@app.route('/reveal_cell_area')
def reveal_cell_area():
    print(game_manager.games)
    game_id = request.args.get('game_id')
    game = game_manager.get_game(game_id)
    
    row = int(request.args.get('row'))
    col = int(request.args.get('col'))
    cell = game.board[row][col]

    game.reveal_cell_area(cell)
       
    response = {
        'board': game.board.to_dict(),
        'game_status': game.status,
    }
    return jsonify(response)
    
@app.route('/toggle_flag')
def toggle_flag():
    game_id = request.args.get('game_id')
    game = game_manager.get_game(game_id)
    
    row = int(request.args.get('row'))
    col = int(request.args.get('col'))

    game.toggle_flag(row, col)
    
    response = {
        'board': game.board.to_dict(),
        'game_status': game.status,
    }
    return jsonify(response)
    
if __name__ == '__main__':
    app.run(port=8000)
    #~ app.run(host='192.168.1.14', port=5010)
    

    
    
    
    
    
    
    
