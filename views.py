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

from minesweeper import Game, GameManager

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']

game_manager = GameManager()

@app.route('/')
def index(): 
    session['id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/start_new_game')
def start_new_game():
    game = Game()
    
    game_id = game_manager.register_game(game, session)
    game_manager.unregister_old_games()
    
    print('CURRENT GAMES', len(game_manager.games))
    
    response = {
        'current_games_ids': [
            k 
            for k, v in game_manager.games.items()
        ],
        'game_id': game_id,
        'board': game.board.to_dict(),
    }
    return jsonify(response)
    
@app.route('/get_games_state')
def get_games_state():
    current_game_id = request.args.get('game_id')
    current_game = game_manager.get_game(current_game_id)
    
    response = {
        'board': current_game.board.to_dict(),
        'current_games': [
			game_id 
			for game_id, v in game_manager.games.items()
		]
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
    
    if game.end_status:
        game_manager.unregister_game(game_id)
       
    response = {
        'board': game.board.to_dict(),
        'game_status': game.end_status,
    }
    return jsonify(response)
    
@app.route('/toggle_flag')
def toggle_flag():
    game_id = request.args.get('game_id')
    game = game_manager.get_game(game_id)
    
    row = int(request.args.get('row'))
    col = int(request.args.get('col'))

    game.toggle_flag(row, col)
    
    if game.end_status:
        game_manager.unregister_game(game_id)
    
    response = {
        'board': game.board.to_dict(),
        'game_status': game.end_status,
    }
    return jsonify(response)
    
if __name__ == '__main__':
    app.run(port=8000)
    #~ app.run(host='192.168.1.14', port=5010)
    

    
    
    
    
    
    
    
