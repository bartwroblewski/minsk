from flask import (
    Flask, 
    render_template, 
    Response, 
    jsonify,
    request
)
from minesweeper import Game 

app = Flask(__name__)
game = Game()
game.place_mines_randomly()
game.update_neighbours()

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/get_board')
def get_board():
    return jsonify(game.board.to_dict())
    
@app.route('/reveal_cell_area')
def reveal_cell_area():
    row = int(request.args.get('row'))
    col = int(request.args.get('col'))
    
    cell = game.board[row][col]
    
    game.reveal_cell_area(cell)
    return jsonify(game.board.to_dict())
    
@app.route('/place_flag')
def place_flag():
    row = int(request.args.get('row'))
    col = int(request.args.get('col'))
    
    game.place_flag(row, col)
    return jsonify(game.board.to_dict())
    
@app.route('/remove_flag')
def remove_flag():
    row = int(request.args.get('row'))
    col = int(request.args.get('col'))
    
    game.remove_flag(row, col)
    return jsonify(game.board.to_dict())
    
if __name__ == '__main__':
    app.run(port='8000')
    
    
    
    
    
    
    
    
    
    
