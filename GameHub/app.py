import random
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

# --- AI Profile Generator ---
@app.route("/api/generate-ai-profile", methods=["POST"])
def generate_profile():
    prefixes = ["Cyber", "Neon", "Quantum", "Void", "Apex", "Nova"]
    suffixes = ["Ghost", "Titan", "Spectre", "Pulse", "Spark"]
    username = f"{random.choice(prefixes)}_{random.choice(suffixes)}{random.randint(10,99)}"
    return jsonify({"username": username})

# --- Tic-Tac-Toe Minimax AI ---
def check_ttt_winner(board):
    wins = [[0,1,2], [3,4,5], [6,7,8], [0,3,6], [1,4,7], [2,5,8], [0,4,8], [2,4,6]]
    for w in wins:
        if board[w[0]] and board[w[0]] == board[w[1]] == board[w[2]]: return board[w[0]]
    if None not in board: return "Tie"
    return None

def minimax(board, depth, is_max):
    winner = check_ttt_winner(board)
    if winner == "O": return 10 - depth
    if winner == "X": return depth - 10
    if winner == "Tie": return 0

    if is_max:
        best = -float("inf")
        for i in range(9):
            if board[i] is None:
                board[i] = "O"
                best = max(best, minimax(board, depth + 1, False))
                board[i] = None
        return best
    else:
        best = float("inf")
        for i in range(9):
            if board[i] is None:
                board[i] = "X"
                best = min(best, minimax(board, depth + 1, True))
                board[i] = None
        return best

@app.route("/api/tictactoe/move", methods=["POST"])
def tictactoe_move():
    board = request.json.get("board", [None] * 9)
    if check_ttt_winner(board):
        return jsonify({"move": None, "winner": check_ttt_winner(board)})

    best_score, best_move = -float("inf"), None
    for i in range(9):
        if board[i] is None:
            board[i] = "O"
            score = minimax(board, 0, False)
            board[i] = None
            if score > best_score:
                best_score, best_move = score, i

    if best_move is not None: board[best_move] = "O"
    return jsonify({"move": best_move, "winner": check_ttt_winner(board)})

# --- Snakes & Ladders Logic ---
SNAKES_LADDERS = {
    4: 14, 9: 31, 20: 38, 28: 84, 40: 59, 51: 67, 63: 81, 71: 91, # Ladders
    17: 7, 54: 34, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 99: 78  # Snakes
}

@app.route("/api/snakes/roll", methods=["POST"])
def snakes_roll():
    data = request.json or {}
    pos = data.get("pos", 1)
    dice = random.randint(1, 6)
    
    new_pos = pos + dice
    if new_pos > 100:
        new_pos = pos
    else:
        new_pos = SNAKES_LADDERS.get(new_pos, new_pos)
        
    return jsonify({"dice": dice, "new_pos": new_pos, "winner": "Yes" if new_pos == 100 else None})

if __name__ == "__main__":
    app.run(debug=True, port=5000)