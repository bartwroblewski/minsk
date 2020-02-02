import random
import datetime

class NotEnoughBoardCellsError(Exception):
    def __init__(self, n_mines, n_cells):
        self.message = 'You are trying to place {} mines on the board, but there are only {} cells available.'.format(n_mines, n_cells)
        
    def __str__(self):
        return self.message

class GameSettings:
    def __init__(self):
        self.n_rows = 20
        self.n_cols = 20
        self.mines_ratio = 8
        self.n_mines = int(round(
            self.n_rows * self.n_cols / self.mines_ratio
        ))
        #~ self.n_mines = 2

class GameManager:
    def __init__(self):
        self.games = {}
        self.game_timeout = 0.1
        
    def register_game(self, game):
        self.games[game.id_] = game
        
    def unregister_game(self, game):
        del self.games[game.id_]
        
    def get_game(self, game_id):
        return self.games[game_id]
        
    def unregister_old_games(self):
        d = {}
        for game_id, game in self.games.items():
            timedelta = datetime.datetime.now() - game.created_at
            timedelta_in_minutes = timedelta.total_seconds() / 60            
            if timedelta_in_minutes < self.game_timeout:
                d[game_id] = game
        self.games = d

class Game:
    def __init__(self, id_):
        self.id_ = id_
        self.created_at = datetime.datetime.now()
        self.status = None
        self.settings = GameSettings()
        self.board = Board(
            self.settings.n_rows, 
            self.settings.n_cols,
        )
        
        self.place_mines_randomly()
        self.update_neighbours()
        
        self.score = 0
        
    def check_score(self):
        if self.score == self.settings.n_mines:
            self.status = 'won'
        
    def place_mine_randomly(self):
        random_cell = self.board.get_random_cell()
        if random_cell.mined:
            # try again if already mined
            self.place_mine_randomly()
        else:
            random_cell.mine()
    
    def update_neighbours(self):
        for cell in self.board:
            if cell.mined:
                neighbours = self.board.get_cell_neighbours(cell)
                for n in neighbours:
                    n.value += 1 
        
    def place_mines_randomly(self):
        if self.settings.n_mines > self.board.n_cells:
            raise NotEnoughBoardCellsError(self.settings.n_mines, self.n_cells)
            
        for i in range(self.settings.n_mines):
            self.place_mine_randomly()
    
    def toggle_flag(self, row, col):
        cell = self.board[row][col]
        
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
                self.status = 'lost'
                self.reveal_all_cells()
            else:
                cell.hidden = False
                
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
    
    def reveal_all_cells(self):
        for cell in self.board:
            cell.hidden = False

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.value = 0
        
        self.hidden = True
        self.mined = False
        self.flagged = False
        
    def unhide(self):
        if self.mined:
            return 'You stepped on a mine!'
        self.hidden = False
        
    def flag(self):
        self.flagged = True
        
    def unflag(self):
        self.flagged = False
    
    def mine(self):
        self.mined = True
        
    def symbol(self):
        if self.hidden and not self.flagged:
            return ''
        elif not self.hidden:
            if self.value == 0 and not self.mined:
                return ''
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
    EMPTY_SYMBOL = 'x'
    MINE_SYMBOL = 'm'
    FLAG_SYMBOL = 'f'
    
    def __init__(self, n_rows, n_cols):
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.n_cells = n_rows * n_cols 
        self.board = self.get_board()
        
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
        
    def contains(self, row, col):
        if 0 <= row <= (self.n_rows - 1) and 0 <= col <= (self.n_cols - 1):
            return True
            
    def __str__(self):
        return '\n'.join(str(row) for row in self.board)
        
    def __getitem__(self, i):
        return self.board[i]
        
    def __iter__(self):
        for row in self.board:
            for cell in row:
                yield cell
        
    def show_values(self):
        for row in self.board:
            s = ' '.join(str(cell.value) for cell in row)
            print(s)
        print('\n')
        
    def show_symbols(self):
        # print(' '.join(str(i) for i in range(self.n_cols)))
        for row in self.board:
            s = ' '.join(str(cell.symbol()) for cell in row)
            print(s)
        print('\n')
        
    def as_string(self):
        s = ''
        for row in self.board:
            s += ' '.join(str(cell.symbol()) for cell in row)
            s += '\n'
        print(s)
        return s
                
    def to_dict(self):
        d = {
            'n_rows': self.n_rows,
            'n_cols': self.n_cols,
            #~ 'cells': [cell.to_dict() for row in self.board for cell in row],
            'rows': [[cell.to_dict() for cell in row] for row in self.board],
        }
        return d

def main():
    game = Game()
    game.place_mines_randomly()
    game.update_neighbours()
    
    while True:
        game.board.show_symbols()
        
        action = input('reveal or flag (r/f)?')
        row, col = input('row, col').split(' ')
        cell = game.board[int(row)][int(col)]
        
        if action == 'r':
            game.reveal_cell_area(cell)
        if action == 'f':
            game.place_flag(cell.row, cell.col)
    
if __name__ == '__main__':
    main()
    
