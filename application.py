from flask import Flask, render_template, session, redirect, url_for
from flask_session import Session
from tempfile import mkdtemp
import math

app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Keep track history
history = []

def get_winner():
    board = session["board"]
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

        # Vertical
        if board[0][i] == board[1][i] and board[0][i] == board[2][i]:  
            winner = board[0][i]

    # Check open spots
    open_spots = 0
    for row in board:
        open_spots += row.count(None)

    if winner == None and open_spots == 0:
        return "tie"
    else:
        return winner

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

        if not history:
            history.append(session["board"])
    
    winner = get_winner()

    return render_template("game.html", game=session["board"], turn=session["turn"], winner=winner, num_history=len(history))

@app.route("/play/<int:row>/<int:col>")
def play(row, col):
    session["board"][row][col] = session["turn"]
    history.append(session["board"]) 
    switch_turn()

    return redirect(url_for("index"))

@app.route("/reset")
def reset():
    del session["board"]
    del session["turn"]
    history.clear()

    return redirect(url_for("index"))

@app.route("/undo")
def undo_move():
    if len(history) > 1:
        history.pop()
        session["board"] = history[-1]
        switch_turn()

    return redirect(url_for("index"))  