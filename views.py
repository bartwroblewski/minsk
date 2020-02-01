from flask import (
    Flask, 
    render_template, 
    Response, 
    jsonify,
    request
)
from minesweeper import Game 

app = Flask(__name__)
game = None

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/start_new_game')
def start_new_game():
    game = Game()
    return jsonify(game.board.to_dict())
    
@app.route('/reveal_cell_area')
def reveal_cell_area():
    row = int(request.args.get('row'))
    col = int(request.args.get('col'))
    
    cell = game.board[row][col]

    game.reveal_cell_area(cell)
    return jsonify(game.board.to_dict())
    
@app.route('/toggle_flag')
def toggle_flag():
    row = int(request.args.get('row'))
    col = int(request.args.get('col'))
    
    game.toggle_flag(row, col)
    return jsonify(game.board.to_dict())
    
if __name__ == '__main__':
    app.run(port='8000')
    
    
    
    
    
    
    
    
    
