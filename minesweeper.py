import random
import datetime
import uuid

class NotEnoughBoardCellsError(Exception):
    def __init__(self, n_mines, n_cells):
        self.message = 'You are trying to place {} mines on the board, but there are only {} cells available.'.format(n_mines, n_cells)
        
    def __str__(self):
        return self.message

class GameSettings:
    settings_per_difficulty = {
        'easy': {'n_rows': 10, 'n_cols': 10, 'n_mines': 5},
        'normal': {'n_rows': 20, 'n_cols': 20, 'n_mines': 30},
        'hard': {'n_rows': 30, 'n_cols': 30, 'n_mines': 100},
    }
            
    def __init__(self, difficulty='normal'):
        self.n_rows = self.settings_per_difficulty[difficulty]['n_rows']
        self.n_cols = self.settings_per_difficulty[difficulty]['n_cols']
        self.n_mines = self.settings_per_difficulty[difficulty]['n_mines']
                

class GamesManager:
    def __init__(self):
        self.games = {}
        self.game_expiration = 20 # in seconds
        
    def register_game(self, game):
        game_id = str(uuid.uuid4())
        self.games[game_id] = {
            'game': game,
            'created_at': datetime.datetime.now(),
        }
        return game_id
    
    def get_secs_to_game_expire(self, game_id):
        game = self.games[game_id]
        secs_to_expire = (self.game_expiration - (datetime.datetime.now() - game['created_at']).total_seconds())
        return round(secs_to_expire)
        
    def unregister_game(self, game_id):
        del self.games[game_id]
        
    def get_game(self, game_id):
        game = self.games.get(game_id)
        if game:        
            # reset game expiration
            game['created_at'] = datetime.datetime.now()
            return game['game']
                    
    def get_nonexpired_games(self):
        nonexpired_games = []
        for k, v in self.games.items():
            secs_to_expire = self.get_secs_to_game_expire(k)
            if secs_to_expire > 0:
                d = {}
                d['secs_to_expire'] = secs_to_expire
                d['completion'] = str(self.games[k]['game'].check_completion())
                d['id'] = k
                nonexpired_games.append(d)
        #~ nonexpired_sorted_by_secs = sorted(nonexpired_games, key=lambda x: x['secs_to_expire'])
        return nonexpired_games
       
class Game:
    def __init__(self, difficulty="normal"):      
        self.settings = GameSettings(difficulty)
        self.board = Board(
            self.settings.n_rows, 
            self.settings.n_cols,
            self.settings.n_mines,
        )
        
        self.end_status = None
        self.revealed_cells = []
        self.score = 0
        
    def toggle_flag(self, cell):        
        if not cell.hidden:
            return 'Cannot flag/unflag an already revealed cell!'
            
        if cell.flagged:
            cell.flagged = False
            if cell.mined:
                self.score -= 1
        else:
            cell.flagged = True
            if cell.mined:
                self.score += 1           
            self.check_score()
            
    def reveal_cell_area(self, cell):
        if not cell.flagged:
            if cell.mined:
                self.end_status = 'You stepped on a mine!'
                self.reveal_all_cells()
            else:
                cell.hidden = False
                self.revealed_cells.append(cell)
                
                adjacent = (
                    (cell.row - 1, cell.col),
                    (cell.row, cell.col + 1),
                    (cell.row + 1, cell.col),
                    (cell.row, cell.col - 1),
                )
                for row, col in adjacent:
                    if self.board.contains(row, col):
                        adjacent_cell = self.board[row][col]
                        if cell.value == 0 and adjacent_cell.hidden and not adjacent_cell.mined:
                            self.reveal_cell_area(adjacent_cell)
            
            # end game if all unmined cells revealed
            if self.board.n_cells - len(self.revealed_cells) == self.settings.n_mines:
                self.score = self.settings.n_mines
                self.check_score()
    
    def reveal_all_cells(self):
        for cell in self.board:
            #~ if not cell.flagged and not cell.mined:
            cell.hidden = False
        
    def check_score(self):
        if self.score == self.settings.n_mines:
            self.end_status = 'You win!'
            self.reveal_all_cells()
            
    def check_completion(self):   
        #~ return (self.score / self.settings.n_mines) * 100 
        return round((len(self.revealed_cells) / self.board.n_cells) * 100) 
                
class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.value = 0
        
        self.hidden = True
        self.mined = False
        self.flagged = False
                
    def symbol(self, custom_empty_symbol=None):
        if self.hidden and not self.flagged:
            return custom_empty_symbol or ''
        elif not self.hidden:
            if self.value == 0 and not self.mined:
                return custom_empty_symbol or ''
            elif self.mined:
                return 'M'
            else:
                return self.value    
        else:
            return 'F'
        
    def to_dict(self):
        d = {
            'row': str(self.row),
            'col': str(self.col),
            'hidden': self.hidden,
            'mined': self.mined,
            'flagged': self.flagged,
            'symbol': self.symbol(),
            'value': self.value,
        }
        return d
        
class Board:    
    def __init__(self, n_rows, n_cols, n_mines):
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.n_cells = n_rows * n_cols 
        self.n_mines = n_mines
        self.board = self.get_board()
        
        self.place_mines_randomly()
        self.update_neighbours()
        
    def get_board(self):
        board = []
        for n_row in range(self.n_rows):
            row = [
                Cell(n_row, n_col)
                for n_col in range(self.n_cols)
            ]
            board.append(row)
        return board
    
    def get_random_cell(self):
        random_row = random.randint(0, self.n_rows - 1)
        random_col = random.randint(0, self.n_cols - 1)
        return self.board[random_row][random_col]
                    
    def get_cell_neighbours(self, cell):
        neighbours_coors = (
            (cell.row -1, cell.col -1),
            (cell.row -1, cell.col),
            (cell.row -1, cell.col + 1),
            (cell.row, cell.col - 1),
            (cell.row, cell.col + 1),
            (cell.row + 1, cell.col - 1),
            (cell.row + 1, cell.col),
            (cell.row + 1, cell.col + 1),
        )
        for row, col in neighbours_coors:
            if self.contains(row, col): 
                yield self.board[row][col] 
                
    def update_neighbours(self):
        for cell in self:
            if cell.mined:
                neighbours = self.get_cell_neighbours(cell)
                for n in neighbours:
                    n.value += 1 
        
    def contains(self, row, col):
        '''Check if the given row/cell combination
        lies within the board.
        '''
        if 0 <= row <= (self.n_rows - 1) and 0 <= col <= (self.n_cols - 1):
            return True
            
    def place_mine_randomly(self):
        random_cell = self.get_random_cell()
        if random_cell.mined:
            # try again if already mined
            self.place_mine_randomly()
        else:
            random_cell.mined = True
        
    def place_mines_randomly(self):
        if self.n_mines > self.n_cells:
            raise NotEnoughBoardCellsError(self.n_mines, self.n_cells)
            
        for i in range(self.n_mines):
            self.place_mine_randomly()
                   
    def __getitem__(self, i):
        return self.board[i]
        
    def __iter__(self):
        for row in self.board:
            for cell in row:
                yield cell
                 
    def to_dict(self):
        d = {
            'n_rows': self.n_rows,
            'n_cols': self.n_cols,
            'rows': [[cell.to_dict() for cell in row] for row in self.board],
        }
        return d
        
    def show_symbols(self):
        '''Display of offline mode'''
        for row in self.board:
            s = ' '.join(str(cell.symbol('X')) for cell in row)
            print(s)
        print('\n')

def main():
    # OFFLINE VERSION, UNDER CONSTRUCTION
    game = Game()
    game.board.place_mines_randomly()
    game.board.update_neighbours()
    
    while True:
        game.board.show_symbols()
        
        action = input('Reveal or flag (r/f)?')
        row, col = input('Row, col?').split(' ')
        cell = game.board[int(row)][int(col)]
        
        if action == 'r':
            game.reveal_cell_area(cell)
        if action == 'f':
            game.toggle_flag(cell)
        
        game.check_score()
        print(game.end_status)
        if game.end_status:
            print(game.end_status)
            break
    
if __name__ == '__main__':
    main()
