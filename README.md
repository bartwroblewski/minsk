# minsk
Live version [here](http://46.101.156.79:8000/).

![Alt text](/screenshots/app.png?raw=true)

## About

A multiplayer implementation of the popular Minesweeper game.

## Usage

You can start a new game and wait for others to join or join someone else's game.

Each game expires after some time of inactivity.

## Technology stack

Backend: Python & Flask. Flask SocketIO is used to handle websockets connection and broadcast board changes to other players of the same game.

Frontend: vanilla JavaScript.
