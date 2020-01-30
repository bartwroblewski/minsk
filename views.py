from flask import Flask, Response, jsonify

from minesweeper import Game

app = Flask(__name__)
game = Game()

@app.route('/')
def index():
    game.place_mines_randomly()
    game.update_neighbours()
    cell = game.board[0][0]
    game.reveal_cell_area(cell)
    return Response(
        game.board.as_string(), 
        mimetype='text/plain',
    )
if __name__ == '__main__':
    app.run()
