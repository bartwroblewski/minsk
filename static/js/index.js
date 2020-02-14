class Model {
    constructor() {
        this.game_id = ''
    }
}

class View {
    constructor() {
        this.board = document.getElementById('board')
        this.new_game_button = document.getElementById('new_game_button')
        this.current_games_list = document.getElementById('current_games_list')
        this.end_status = document.getElementById('end_status')
        this.difficulty_select = document.getElementById('difficulty_select')
    }
    
    drawBoard(board) {
        let n_rows = board.n_rows
        let n_cols = board.n_cols
        let cells = board.cells
        let rows = board.rows
        console.log('drawing board', board)
        
        this.board.innerHTML = ''
        
        rows.forEach(row => {
            let tr = document.createElement('tr')
            row.forEach(cell => {
                let td = document.createElement('td')
                td.textContent = cell.symbol
                if (cell.hidden) {
                    td.classList.add('grey')
                }
                td.id = cell.col
                tr.appendChild(td)
            })
            this.board.appendChild(tr)
        })
    }
    
    drawGamesList(current_games, game_id) {
        console.log('DRAWING GAMES LIST', current_games)
        this.current_games_list.innerHTML = ''
        
        current_games.forEach(game => {
            let li = document.createElement('li')
            li.id = game.id
            
            if (game.id === game_id) {
                li.style.color = 'green'
            } else {
                li.style.color = ''
            }
            li.textContent = 
                `Game completed in: ${game.completion}%,
                expires in: ${game.secs_to_expire} seconds;`

            this.current_games_list.appendChild(li)
        })
    }
                
    bindGamesListItemClicked(handler) {
        this.current_games_list.addEventListener('click', e => {
            this.end_status.textContent = ''
            let game_id = e.target.id
            handler(game_id)
        })
    }
    
    bindNewGameClick(handler) {
        this.new_game_button.addEventListener('click', e => {
            this.end_status.textContent = ''
            handler()
        })
    }
    
    bindBoardClick(handler) {   
        this.board.addEventListener('click', e => {
            let row = e.target.parentElement.rowIndex
            let col = e.target.id
            handler(row, col)
        })
    }
    
    bindBoardContextMenu(handler) {
        this.board.addEventListener('contextmenu', e => {
            e.preventDefault()
            let row = e.target.parentElement.rowIndex
            let col = e.target.id
            handler(row, col)
        })
    }
}

class Controller {
    constructor(model, view, socket) {
        this.model = model
        this.view = view
        this.socket = socket
        
        this.view.bindNewGameClick(this.handleNewGameClick)
        this.view.bindBoardClick(this.handleBoardClick)
        this.view.bindBoardContextMenu(this.handleContextMenu)
        this.view.bindGamesListItemClicked(this.handleGamesListItemClicked)
        
        //~ this.socket.on('connect', () => {
            //~ socket.emit('socket_connected', {data: 'Im connected!'})
        //~ })
        
        this.startNewGame()
        fetch(refresh_games_list_periodically_url)
        
        
        this.socket.on('new_game_started', response => {
            this.model.game_id = response['game_id']
            this.view.drawBoard(response['board'])      
            this.refreshGamesList()
        })
        
        this.socket.on('games_list_refreshed', (response) => {
            this.view.drawGamesList(response['games_list'], this.model.game_id)
        })
        
        this.socket.on('game_switched', response => {
            this.model.game_id = response['game_id']
            this.view.drawBoard(response['board'])
            this.refreshGamesList()
        })
            
        this.socket.on('board_changed', response => {
            if (this.model.game_id === response['game_id']) {
                app.view.drawBoard(response['board'])
                if (response.end_status) {
                    this.view.end_status.textContent = response.end_status
                }   
            }
            this.refreshGamesList()
        })
    }
    
    handleGamesListItemClicked = game_id => {
        this.socket.emit('switch_game', {
            'game_id': game_id,
        })
    }
    
    handleNewGameClick = () => {
        this.startNewGame()
    }
    
    handleBoardClick = (row, col) => {
        this.boardMove(row, col, 'reveal_cell_area')
    }
    
    handleContextMenu = (row, col) => {
        this.boardMove(row, col, 'toggle_flag')
    }
    
    startNewGame = () => {
        this.socket.emit('start_new_game', {
            'difficulty': this.view.difficulty_select.value,
        })
    }
    
    refreshGamesList = () => {
        this.socket.emit('refresh_games_list')
    }
    
    boardMove = (row, col, move_name) => {
        this.socket.emit('board_move', {
            row: row,
            col: col,
            game_id: this.model.game_id,
            move_name: move_name,
        })
    }
}

let app = new Controller(new Model(), new View(), io())
