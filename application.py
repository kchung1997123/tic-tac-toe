from flask import Flask, render_template, session, redirect, url_for
from flask_session import Session
from tempfile import mkdtemp
import math
import copy

app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def get_winner(board):
    winner = None

    # Diagonal
    if board[0][0] == board[1][1] and board[0][0] == board[2][2]:
        winner = board[0][0]

    # Diagonal
    if board[0][2] == board[1][1] and board[0][2] == board[2][0]:
        winner = board[0][2]

    for i in range(3):
        # Horizontal
        if board[i][0] == board[i][1] and board[i][0] == board[i][2]:
            winner = board[i][0]
            break

        # Vertical
        if board[0][i] == board[1][i] and board[0][i] == board[2][i]:  
            winner = board[0][i]
            break

    # Check open spots
    open_spots = 0
    for row in board:
        open_spots += row.count(None)

    if winner == None and open_spots == 0:
        return "tie"
    else:
        return winner

def get_score(winner):
    if winner == "X":
        return 1
    elif winner == "O":
        return -1
    else:
        return 0

def minimax(game, turn):
    winner = get_winner(game)
    if winner != None:
        return get_score(winner)

    board = session["board"]

    if turn == "X":
        best_score = -math.inf
    else:
        best_score = math.inf

    for i in range(3):
        for j in range(3):
            if board[i][j] == None:
                board[i][j] = turn

                if turn == "X":
                    score = minimax(board, "O")
                    best_score = max(best_score, score)
                else:
                    score = minimax(board, "X")
                    best_score = min(best_score, score)
                
                board[i][j] = None

    return best_score

def switch_turn():
    if session["turn"] == "X":
        session["turn"] = "O"
    else:
        session["turn"] = "X"

@app.route("/")
def index():
    if "board" not in session:
        session["board"] = [[None, None, None], [None, None, None], [None, None, None]]
        session["turn"] = "X"
        session["history"] = []

        if not session["history"]:
            session["history"].append(copy.deepcopy(session["board"]))

    winner = get_winner(session["board"])

    return render_template("game.html", game=session["board"], turn=session["turn"], winner=winner, num_history=len(session["history"]))

@app.route("/play/<int:row>/<int:col>")
def play(row, col):
    session["board"][row][col] = session["turn"]
    session["history"].append(copy.deepcopy(session["board"]))
    switch_turn()

    return redirect(url_for("index"))

@app.route("/reset")
def reset():
    del session["board"]
    del session["turn"]
    del session["history"]

    return redirect(url_for("index"))

@app.route("/undo")
def undo_move():
    if len(history) > 1:
        history.pop()
        session["board"] = session["history"][-1]
        switch_turn()

    return redirect(url_for("index"))  

@app.route("/best")
def best_move():    
    move = [None, None]
    board = session["board"]

    if session["turn"] == "X":
        best_score = -math.inf
    else:
        best_score = math.inf

    for i in range(3):
        for j in range(3):
            if board[i][j] == None:
                board[i][j] = session["turn"]

                if session["turn"] == "X":
                    score = minimax(board, "O")
                    if score > best_score:
                        best_score = score
                        move = [i, j]
                else:
                    score = minimax(board, "X")
                    if score < best_score:
                        best_score = score
                        move = [i, j]
                
                board[i][j] = None

    play(move[0], move[1])  

    return redirect(url_for("index"))
