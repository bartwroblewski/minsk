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

from minesweeper import Game, GamesManager

games_manager = GamesManager()

app = Flask(__name__)
    
@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/start_new_game')
def start_new_game():
    game = Game()   
    game_id = games_manager.register_game(game)

    response = {
        'game_id': game_id,
        'board': game.board.to_dict(),
    }
    return jsonify(response)
    
@app.route('/get_game_board')
def get_game_board():
	game_id = request.args.get('game_id')
	game = games_manager.get_game(game_id)
	
	if game.end_status:
        games_manager.unregister_game(game_id)
        
	response = {
		'board': game.board.to_dict(),
		'end_status': game.end_status,
	}
	return jsonify(response)
    
@app.route('/get_current_games')
def get_current_games():
        d = games_manager.get_current_games()
        current_games = [
        {
            'id': k,
            'started_ago': round((datetime.datetime.now() - d[k]['game_creation_date']).total_seconds() / 60),
            'completion': d[k]['game'].completion(),
        }
        for k, v in d.items()
    ]
        response = {'current_games': current_games}
        return jsonify(response)
    
@app.route('/move')
def move():
    game_id = request.args.get('game_id')
    game = games_manager.get_game(game_id)
    
    row = int(request.args.get('row'))
    col = int(request.args.get('col'))
    cell = game.board[row][col]
    
    move_name = request.args.get('move_name')
    if move_name == 'reveal_cell_area':
        game.reveal_cell_area(cell)       
    if move_name == 'toggle_flag':
        game.toggle_flag(row, col)
    
    #~ if game.end_status:
        #~ games_manager.unregister_game(game_id)
        
    response = {
        'board': game.board.to_dict(),
        'end_status': game.end_status,
    }
    return jsonify(response)
        
# @app.route('/reveal_cell_area')
# def reveal_cell_area():
    # game_id = request.args.get('game_id')
    # game = games_manager.get_game(game_id)
    
    # row = int(request.args.get('row'))
    # col = int(request.args.get('col'))
    # cell = game.board[row][col]

    # game.reveal_cell_area(cell)
    
    # if game.end_status:
        # games_manager.unregister_game(game_id)
                
    # response = {
        # 'board': game.board.to_dict(),
        # 'end_status': game.end_status,
    # }
    # return jsonify(response)
    
# @app.route('/toggle_flag')
# def toggle_flag():
    # game_id = request.args.get('game_id')
    # game = games_manager.get_game(game_id)
    
    # row = int(request.args.get('row'))
    # col = int(request.args.get('col'))

    # game.toggle_flag(row, col)
    
    # if game.end_status:
        # games_manager.unregister_game(game_id)

    # response = {
        # 'board': game.board.to_dict(),
        # 'end_status': game.end_status,
    # }
    # return jsonify(response)
    
@app.route('/get_games_state')
def get_games_state():
    '''Returns data required for live updates:
        1. List of active (i.e. with non-expired session) games; 
        2. The board for the currently played game.
    '''
   # games_manager.unregister_old_games()
    
    current_games = [
        {
            'id': g.id_,
            'started_ago': round((datetime.datetime.now() - g.created_at).total_seconds() / 60),
            'completion': g.completion(),
        }
        for g in all_games
    ]

    current_game_id = request.args.get('game_id')
    # current_game = games_manager.get_game(current_game_id)
    if all_games:
        for g in all_games:
            if g.id_ == current_game_id:
                current_game = g
            else: 
                current_game = None
    else:
        current_game = None
    
    response = {'current_games': current_games}
    if current_game:
        response['board'] = current_game.board.to_dict()
    if not session:
        response['end_status'] = 'Your session has expired! Please reload the page.'
    
    return jsonify(response)
    
    
if __name__ == '__main__':
    app.run(port=8000)
    # app.run(host='192.168.1.14', port=5010)
