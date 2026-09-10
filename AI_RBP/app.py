import random
import copy
import math
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# --- 9x9 CLASSIC SUDOKU PUZZLE BANK ---
SUDOKU_PUZZLES = {
    "easy": [
        [
            [5,3,0,0,7,0,0,0,0], [6,0,0,1,9,5,0,0,0], [0,9,8,0,0,0,0,6,0],
            [8,0,0,0,6,0,0,0,3], [4,0,0,8,0,3,0,0,1], [7,0,0,0,2,0,0,0,6],
            [0,6,0,0,0,0,2,8,0], [0,0,0,4,1,9,0,0,5], [0,0,0,0,8,0,0,7,9]
        ],
        [
            [0,0,0,2,6,0,7,0,1], [6,8,0,0,7,0,0,9,0], [1,9,0,0,0,4,5,0,0],
            [8,2,0,1,0,0,0,4,0], [0,0,4,6,0,2,9,0,0], [0,5,0,0,0,3,0,2,8],
            [0,0,9,3,0,0,0,7,4], [0,4,0,0,5,0,0,3,6], [7,0,3,0,1,8,0,0,0]
        ]
    ],
    "medium": [
        [
            [0,2,0,6,0,8,0,0,0], [5,8,0,0,0,9,7,0,0], [0,0,0,0,4,0,0,0,0],
            [3,7,0,0,0,0,5,0,0], [6,0,0,0,0,0,0,0,4], [0,0,8,0,0,0,0,1,3],
            [0,0,0,0,2,0,0,0,0], [0,0,9,8,0,0,0,3,6], [0,0,0,3,0,6,0,9,0]
        ]
    ],
    "hard": [
        [
            [1,0,0,0,0,7,0,9,0], [0,3,0,0,2,0,0,0,8], [0,0,9,6,0,0,5,0,0],
            [0,0,5,3,0,0,9,0,0], [0,1,0,0,8,0,0,0,2], [6,0,0,0,0,4,0,0,0],
            [3,0,0,0,0,0,0,1,0], [0,4,0,0,0,0,0,0,7], [0,0,7,0,0,0,3,0,0]
        ]
    ]
}

# --- SUDOKU SOLVER LOGIC ---
def is_valid_sudoku(board, row, col, num):
    for i in range(9):
        if (i != col and board[row][i] == num) or (i != row and board[i][col] == num):
            return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            r, c = start_row + i, start_col + j
            if (r != row or c != col) and board[r][c] == num:
                return False
    return True

def solve_sudoku_grid(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid_sudoku(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku_grid(board):
                            return True
                        board[row][col] = 0
                return False
    return True

# --- DYNAMIC MAP COLORING LOGIC ---
class DynamicMapColoringAI:
    def __init__(self, vertices, adjacency_matrix):
        self.V = vertices
        self.graph = adjacency_matrix
        self.colors_map = {1: "#ef4444", 2: "#10b981", 3: "#3b82f6", 4: "#eab308", 5: "#a855f7", 6: "#ec4899"}

    def is_safe(self, v, color_assigned, current_color):
        for i in range(self.V):
            if self.graph[v][i] == 1 and color_assigned[i] == current_color:
                return False
        return True

    def solve_util(self, num_colors, color_assigned, v):
        if v == self.V:
            return True
        for c in range(1, num_colors + 1):
            if self.is_safe(v, color_assigned, c):
                color_assigned[v] = c
                if self.solve_util(num_colors, color_assigned, v + 1):
                    return True
                color_assigned[v] = 0
        return False

    def solve(self, num_colors):
        color_assigned = [0] * self.V
        if not self.solve_util(num_colors, color_assigned, 0):
            return None
        return [self.colors_map.get(c, "#64748b") for c in color_assigned]

def build_grid_adjacency(n):
    cols = 2 if n <= 4 else (3 if n <= 9 else 4)
    graph = [[0] * n for _ in range(n)]
    for i in range(n):
        r_i, c_i = i // cols, i % cols
        for j in range(i + 1, n):
            r_j, c_j = j // cols, j % cols
            # Connected if adjacent vertically or horizontally
            if abs(r_i - r_j) + abs(c_i - c_j) == 1:
                graph[i][j] = 1
                graph[j][i] = 1
    return graph

bus_seats = {i: None for i in range(10)}

# --- COMBINED CSS + HTML INLINE TEMPLATE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI CSP Interactive Hub</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.75);
            --border-color: rgba(255, 255, 255, 0.12);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-blue: #3b82f6;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --accent-yellow: #eab308;
            --accent-purple: #a855f7;
        }

        * { box-sizing: border-box; font-family: 'Inter', -apple-system, sans-serif; }
        body { background: radial-gradient(circle at top, #1e293b, #0f172a); color: var(--text-main); margin: 0; padding: 30px 20px; min-height: 100vh; }
        
        .header { text-align: center; margin-bottom: 24px; }
        h1 { font-size: 2.2rem; font-weight: 800; margin: 0 0 8px 0; }
        h1 span { background: linear-gradient(135deg, #60a5fa, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        p.sub-title { color: var(--text-muted); margin: 0; font-size: 0.95rem; }

        /* TOOL SELECTION SCREEN NAV */
        .tool-selector { display: flex; justify-content: center; gap: 12px; margin: 24px auto 32px auto; max-width: 700px; }
        .nav-tab { flex: 1; padding: 14px 16px; background: rgba(30, 41, 59, 0.5); border: 1px solid var(--border-color); color: var(--text-muted); border-radius: 12px; font-weight: 700; cursor: pointer; transition: all 0.3s; text-align: center; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .nav-tab:hover { background: rgba(255, 255, 255, 0.08); color: #fff; transform: translateY(-2px); }
        .nav-tab.active { background: linear-gradient(135deg, #2563eb, #3b82f6); color: #fff; border-color: #60a5fa; box-shadow: 0 4px 20px rgba(59, 130, 246, 0.4); }

        .tool-view { display: none; max-width: 680px; margin: 0 auto; }
        .tool-view.active { display: block; animation: fadeIn 0.3s ease-in-out; }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

        .card { background: var(--card-bg); backdrop-filter: blur(12px); border: 1px solid var(--border-color); padding: 28px; border-radius: 20px; box-shadow: 0 15px 35px -10px rgba(0,0,0,0.6); }
        .card h2 { font-size: 1.4rem; border-bottom: 1px solid var(--border-color); padding-bottom: 14px; margin-top: 0; display: flex; justify-content: space-between; align-items: center; }

        .control-row { display: flex; gap: 10px; align-items: center; margin-bottom: 16px; flex-wrap: wrap; }
        .control-group { flex: 1; min-width: 140px; }
        label { display: block; font-size: 0.8rem; color: var(--text-muted); margin-bottom: 4px; font-weight: 600; }

        button { background: linear-gradient(135deg, #3b82f6, #2563eb); color: #fff; border: none; padding: 11px 16px; border-radius: 10px; cursor: pointer; font-weight: 600; transition: all 0.2s; width: 100%; }
        button:hover { filter: brightness(1.15); transform: translateY(-1px); }
        .btn-secondary { background: rgba(255, 255, 255, 0.08); color: #cbd5e1; border: 1px solid var(--border-color); }
        .btn-hint { background: linear-gradient(135deg, #eab308, #ca8a04); color: #0f172a; }
        .btn-group { display: flex; gap: 10px; margin-top: 14px; }

        input[type="text"], select { width: 100%; padding: 10px 12px; background: rgba(15, 23, 42, 0.7); border: 1px solid var(--border-color); color: #f8fafc; border-radius: 10px; outline: none; font-size: 0.95rem; }

        /* SUDOKU GRID */
        .sudoku-board { display: grid; grid-template-columns: repeat(9, 1fr); gap: 4px; background: rgba(15, 23, 42, 0.9); padding: 10px; border-radius: 12px; border: 1px solid var(--border-color); margin-top: 12px; }
        .sudoku-board input { width: 100%; height: 42px; text-align: center; background: rgba(30, 41, 59, 0.9); border: 1px solid rgba(255,255,255,0.08); color: #f8fafc; font-weight: 700; font-size: 1.1rem; border-radius: 6px; outline: none; }
        .sudoku-board input.correct { background: rgba(16, 185, 129, 0.25) !important; color: #34d399 !important; border-color: var(--accent-green) !important; }
        .sudoku-board input.wrong { background: rgba(239, 68, 68, 0.25) !important; color: #fca5a5 !important; border-color: var(--accent-red) !important; }

        /* DYNAMIC MAP COLORING GRID */
        .color-palette { display: flex; gap: 10px; margin: 12px 0; align-items: center; background: rgba(15, 23, 42, 0.4); padding: 10px 14px; border-radius: 10px; border: 1px solid var(--border-color); }
        .color-swatch { width: 32px; height: 32px; border-radius: 50%; cursor: pointer; border: 2px solid transparent; transition: transform 0.2s; }
        .color-swatch.active { transform: scale(1.2); border-color: #fff; box-shadow: 0 0 10px rgba(255,255,255,0.4); }

        .dynamic-map-grid { display: grid; gap: 12px; margin-top: 16px; background: rgba(15, 23, 42, 0.6); padding: 16px; border-radius: 14px; border: 1px solid var(--border-color); }
        .map-box { height: 80px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.1rem; color: #fff; border: 2px solid rgba(255,255,255,0.15); cursor: pointer; transition: all 0.3s; text-shadow: 0 2px 4px rgba(0,0,0,0.6); }
        .map-box:hover { transform: scale(1.03); border-color: #fff; }

        /* BUS SEAT GRID */
        .bus-layout { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-top: 14px; }
        .seat { padding: 14px; border-radius: 10px; background: rgba(15, 23, 42, 0.6); text-align: center; font-size: 0.85rem; cursor: pointer; border: 1px solid var(--border-color); transition: all 0.2s; }
        .seat:hover { background: rgba(255,255,255,0.08); }
        .seat.booked { background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(225, 29, 72, 0.3)); border-color: var(--accent-red); color: #fca5a5; font-weight: 700; }

        .msg-box { font-size: 0.85rem; font-weight: 600; min-height: 42px; margin-top: 14px; padding: 10px 14px; border-radius: 10px; display: flex; align-items: center; }
        .msg-box.success { color: #6ee7b7; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); }
        .msg-box.error { color: #fca5a5; background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); }
        .hint { font-size: 0.8rem; color: var(--text-muted); margin-top: 8px; }
    </style>
</head>
<body>

    <div class="header">
        <h1>AI CSP <span>Interactive Hub</span></h1>
        <p class="sub-title">Select a constraint satisfaction tool from the dashboard below</p>
    </div>

    <!-- SELECTION SCREEN NAVIGATION -->
    <div class="tool-selector">
        <div class="nav-tab active" id="tab-sudoku" onclick="switchTool('sudoku')">
            <span>🧩</span> Sudoku Solver
        </div>
        <div class="nav-tab" id="tab-map" onclick="switchTool('map')">
            <span>🎨</span> Map Coloring
        </div>
        <div class="nav-tab" id="tab-bus" onclick="switchTool('bus')">
            <span>🚌</span> Seat Booking
        </div>
    </div>

    <!-- TOOL 1: 9x9 SUDOKU SOLVER -->
    <div class="tool-view active" id="view-sudoku">
        <div class="card">
            <h2>Classic 9x9 Sudoku Solver <span>🧩</span></h2>
            <div class="control-row">
                <div class="control-group">
                    <label>Difficulty</label>
                    <select id="sudokuDifficulty" onchange="loadNewSudoku()">
                        <option value="easy">Easy</option>
                        <option value="medium">Medium</option>
                        <option value="hard">Hard</option>
                    </select>
                </div>
                <div class="control-group" style="align-self: flex-end;">
                    <button class="btn-secondary" onclick="loadNewSudoku()">🔄 New Board</button>
                </div>
            </div>
            
            <div id="sudokuGrid" class="sudoku-board"></div>
            
            <div class="btn-group">
                <button onclick="solveSudoku()">⚡ AI Solve</button>
                <button class="btn-hint" onclick="getSudokuHint()">💡 Hint</button>
                <button class="btn-secondary" onclick="resetCurrentSudoku()">Reset</button>
            </div>
            <p class="hint">* Numbers 1–9 with constraint validation per row, column, and 3x3 block.</p>
        </div>
    </div>

    <!-- TOOL 2: DYNAMIC MAP COLORING -->
    <div class="tool-view" id="view-map">
        <div class="card">
            <h2>Dynamic Map Coloring AI <span>🎨</span></h2>
            <div class="control-row">
                <div class="control-group">
                    <label>Number of Boxes/Regions</label>
                    <select id="boxCount" onchange="renderDynamicMap()">
                        <option value="3">3 Regions</option>
                        <option value="4" selected>4 Regions</option>
                        <option value="6">6 Regions</option>
                        <option value="8">8 Regions</option>
                        <option value="9">9 Regions</option>
                        <option value="12">12 Regions</option>
                    </select>
                </div>
                <div class="control-group">
                    <label>Color Constraint</label>
                    <select id="colorCount">
                        <option value="2">2 Colors Constraint</option>
                        <option value="3" selected>3 Colors Constraint</option>
                        <option value="4">4 Colors Constraint</option>
                    </select>
                </div>
                <div class="control-group" style="align-self: flex-end;">
                    <button onclick="colorMapAI()">AI Auto-Color</button>
                </div>
            </div>

            <div class="color-palette">
                <span class="hint" style="margin:0;">Manual Color:</span>
                <div class="color-swatch active" style="background:#ef4444" onclick="selectPaletteColor('#ef4444', this)"></div>
                <div class="color-swatch" style="background:#10b981" onclick="selectPaletteColor('#10b981', this)"></div>
                <div class="color-swatch" style="background:#3b82f6" onclick="selectPaletteColor('#3b82f6', this)"></div>
                <div class="color-swatch" style="background:#eab308" onclick="selectPaletteColor('#eab308', this)"></div>
                <div class="color-swatch" style="background:#a855f7" onclick="selectPaletteColor('#a855f7', this)"></div>
            </div>

            <div id="dynamicMapGrid" class="dynamic-map-grid"></div>
            <div id="mapWarningMsg" class="msg-box error" style="display:none;"></div>
            
            <div class="btn-group">
                <button class="btn-secondary" onclick="resetMapColors()">Reset Region Colors</button>
            </div>
            <p class="hint">* Neighboring adjacent boxes in the grid must not share the same color.</p>
        </div>
    </div>

    <!-- TOOL 3: BUS SEAT BOOKING -->
    <div class="tool-view" id="view-bus">
        <div class="card">
            <h2>Bus Seat Booking <span>🚌</span></h2>
            <div class="control-row">
                <div class="control-group">
                    <label>Passenger Name</label>
                    <input type="text" id="passengerName" placeholder="Enter name">
                </div>
                <div class="control-group">
                    <label>Preference</label>
                    <select id="seatPref">
                        <option value="window">Window Seat</option>
                        <option value="aisle">Aisle Seat</option>
                    </select>
                </div>
            </div>

            <div class="btn-group">
                <button onclick="bookSeatAI()">Auto-Book AI</button>
                <button class="btn-secondary" onclick="resetBus()">Reset All Seats</button>
            </div>

            <div id="bookingMsg" class="msg-box" style="display:none;"></div>
            <div id="busGrid" class="bus-layout"></div>
        </div>
    </div>

    <script>
        // TOOL SWITCHING SYSTEM
        function switchTool(toolName) {
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tool-view').forEach(v => v.classList.remove('active'));

            document.getElementById(`tab-${toolName}`).classList.add('active');
            document.getElementById(`view-${toolName}`).classList.add('active');
        }

        // --- 9x9 SUDOKU SYSTEM ---
        let currentInitialBoard = [];

        async function loadNewSudoku() {
            const difficulty = document.getElementById("sudokuDifficulty").value;
            const res = await fetch('/api/sudoku_new', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({difficulty})
            });
            const data = await res.json();
            if (data.success) {
                currentInitialBoard = data.board;
                renderSudokuGrid(data.board);
            }
        }

        function renderSudokuGrid(board) {
            const grid = document.getElementById("sudokuGrid");
            grid.innerHTML = "";
            for (let r = 0; r < 9; r++) {
                for (let c = 0; c < 9; c++) {
                    const val = board[r][c];
                    grid.innerHTML += `<input type="number" id="cell_${r}_${c}" value="${val !== 0 ? val : ''}" min="1" max="9" oninput="validateSudokuCell(${r}, ${c})">`;
                }
            }
            validateAllCells();
        }

        function resetCurrentSudoku() { renderSudokuGrid(currentInitialBoard); }

        function getSudokuBoardState() {
            let board = [];
            for (let r = 0; r < 9; r++) {
                let row = [];
                for (let c = 0; c < 9; c++) {
                    let v = document.getElementById(`cell_${r}_${c}`).value;
                    row.push(v === "" ? 0 : parseInt(v));
                }
                board.push(row);
            }
            return board;
        }

        function validateSudokuCell(r, c) {
            const board = getSudokuBoardState();
            const inputEl = document.getElementById(`cell_${r}_${c}`);
            const num = board[r][c];
            inputEl.classList.remove("correct", "wrong");
            if (num === 0 || isNaN(num) || num > 9 || num < 1) return;

            let isDuplicate = false;
            for (let i = 0; i < 9; i++) {
                if (i !== c && board[r][i] === num) isDuplicate = true;
                if (i !== r && board[i][c] === num) isDuplicate = true;
            }
            if (isDuplicate) inputEl.classList.add("wrong");
            else inputEl.classList.add("correct");
        }

        function validateAllCells() {
            for (let r = 0; r < 9; r++) {
                for (let c = 0; c < 9; c++) validateSudokuCell(r, c);
            }
        }

        async function solveSudoku() {
            const board = getSudokuBoardState();
            const res = await fetch('/api/sudoku', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({board})
            });
            const data = await res.json();
            if (data.success) {
                for (let r = 0; r < 9; r++) {
                    for (let c = 0; c < 9; c++) {
                        document.getElementById(`cell_${r}_${c}`).value = data.board[r][c];
                    }
                }
                validateAllCells();
            } else alert(data.message);
        }

        async function getSudokuHint() {
            const board = getSudokuBoardState();
            const res = await fetch('/api/sudoku_hint', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({board})
            });
            const data = await res.json();
            if (data.success) {
                const cell = document.getElementById(`cell_${data.row}_${data.col}`);
                cell.value = data.value;
                validateSudokuCell(data.row, data.col);
            } else alert(data.message);
        }

        // --- DYNAMIC MAP COLORING SYSTEM ---
        let selectedColor = "#ef4444";
        let regionColors = {};

        function selectPaletteColor(hex, el) {
            selectedColor = hex;
            document.querySelectorAll(".color-swatch").forEach(s => s.classList.remove("active"));
            el.classList.add("active");
        }

        function renderDynamicMap() {
            const count = parseInt(document.getElementById("boxCount").value, 10);
            const gridContainer = document.getElementById("dynamicMapGrid");
            gridContainer.innerHTML = "";
            regionColors = {};

            let cols = count <= 4 ? 2 : (count <= 9 ? 3 : 4);
            gridContainer.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;

            for (let i = 0; i < count; i++) {
                regionColors[i] = "#334155";
                gridContainer.innerHTML += `
                    <div id="map_box_${i}" class="map-box" style="background:#334155;" onclick="paintBox(${i})">
                        Region ${i + 1}
                    </div>`;
            }
            document.getElementById("mapWarningMsg").style.display = "none";
        }

        function paintBox(boxId) {
            regionColors[boxId] = selectedColor;
            document.getElementById(`map_box_${boxId}`).style.background = selectedColor;
        }

        async function colorMapAI() {
            const count = parseInt(document.getElementById("boxCount").value, 10);
            const numColors = parseInt(document.getElementById("colorCount").value, 10);
            
            const res = await fetch('/api/map_coloring', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({boxes: count, colors: numColors})
            });
            const data = await res.json();
            const warnBox = document.getElementById("mapWarningMsg");

            if (data.success) {
                warnBox.style.display = "none";
                data.colors.forEach((col, idx) => {
                    regionColors[idx] = col;
                    document.getElementById(`map_box_${idx}`).style.background = col;
                });
            } else {
                warnBox.style.display = "flex";
                warnBox.innerText = `⚠️ ${data.message}`;
            }
        }

        function resetMapColors() { renderDynamicMap(); }

        // --- BUS SEAT BOOKING SYSTEM ---
        function displayBookingMessage(msg, isSuccess) {
            const box = document.getElementById("bookingMsg");
            box.style.display = "flex";
            box.innerText = msg;
            box.className = `msg-box ${isSuccess ? 'success' : 'error'}`;
        }

        async function bookSeatAI() {
            const name = document.getElementById("passengerName").value.trim();
            const preference = document.getElementById("seatPref").value;
            if (!name) { displayBookingMessage("Please enter passenger name first!", false); return; }
            const res = await fetch('/api/book_seat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name, preference})
            });
            const data = await res.json();
            displayBookingMessage(data.message, data.success);
            if (data.seats) renderBus(data.seats);
        }

        async function manualBookSeat(seatId) {
            const name = document.getElementById("passengerName").value.trim();
            if (!name) { displayBookingMessage("Please enter passenger name first!", false); return; }
            const res = await fetch('/api/book_manual_seat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({seat_id: seatId, name: name})
            });
            const data = await res.json();
            displayBookingMessage(data.message, data.success);
            if (data.seats) renderBus(data.seats);
        }

        async function resetBus() {
            const res = await fetch('/api/reset_bus', {method: 'POST'});
            const data = await res.json();
            displayBookingMessage("Bus layout reset successfully.", true);
            renderBus(data.seats);
        }

        function renderBus(seats) {
            const container = document.getElementById("busGrid");
            container.innerHTML = "";
            for (let i = 0; i < 10; i++) {
                const occupant = seats ? seats[i] : null;
                const isBooked = occupant !== null && occupant !== undefined;
                container.innerHTML += `
                    <div class="seat ${isBooked ? 'booked' : ''}" onclick="manualBookSeat(${i})">
                        Seat ${i < 10 ? '0' + i : i} (${i % 2 === 0 ? 'Window' : 'Aisle'})<br>
                        ${isBooked ? occupant : 'Click to Book'}
                    </div>`;
            }
        }

        // INITIALIZE ON LOAD
        loadNewSudoku();
        renderDynamicMap();
        renderBus({});
    </script>
</body>
</html>
"""

# --- ROUTE ENDPOINTS ---
@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/sudoku_new", methods=["POST"])
def api_sudoku_new():
    difficulty = request.json.get("difficulty", "easy").lower()
    puzzle_list = SUDOKU_PUZZLES.get(difficulty, SUDOKU_PUZZLES["easy"])
    return jsonify({"success": True, "board": random.choice(puzzle_list)})

@app.route("/api/sudoku", methods=["POST"])
def api_sudoku():
    board = request.json.get("board")
    solved = copy.deepcopy(board)
    if solve_sudoku_grid(solved):
        return jsonify({"success": True, "board": solved})
    return jsonify({"success": False, "message": "No valid solution found!"})

@app.route("/api/sudoku_hint", methods=["POST"])
def api_sudoku_hint():
    board = request.json.get("board")
    solved = copy.deepcopy(board)
    if solve_sudoku_grid(solved):
        empty_cells = [(r, c) for r in range(9) for c in range(9) if board[r][c] == 0]
        if not empty_cells:
            return jsonify({"success": False, "message": "Sudoku is already complete!"})
        r, c = random.choice(empty_cells)
        return jsonify({"success": True, "row": r, "col": c, "value": solved[r][c]})
    return jsonify({"success": False, "message": "Cannot solve current board!"})

@app.route("/api/map_coloring", methods=["POST"])
def api_map_coloring():
    data = request.json
    num_boxes = int(data.get("boxes", 4))
    num_colors = int(data.get("colors", 3))
    
    graph = build_grid_adjacency(num_boxes)
    ai = DynamicMapColoringAI(num_boxes, graph)
    result = ai.solve(num_colors)
    
    if result:
        return jsonify({"success": True, "colors": result})
    return jsonify({"success": False, "message": f"Cannot color {num_boxes} regions with only {num_colors} colors without conflicts!"})

@app.route("/api/book_seat", methods=["POST"])
def api_book_seat():
    data = request.json
    name = data.get("name", "").strip()
    pref = data.get("preference", "window").lower()
    available = [s for s, occupant in bus_seats.items() if occupant is None]
    if not available:
        return jsonify({"success": False, "message": "Bus is completely full!"})
    target_seats = [s for s in available if (s % 2 == 0 if pref == "window" else s % 2 != 0)]
    seat = target_seats[0] if target_seats else available[0]
    bus_seats[seat] = name
    return jsonify({"success": True, "message": f"AI booked {pref.capitalize()} Seat {seat:02d} for {name}.", "seats": bus_seats})

@app.route("/api/book_manual_seat", methods=["POST"])
def api_book_manual_seat():
    data = request.json
    seat_id = int(data.get("seat_id"))
    name = data.get("name", "").strip()
    current_occupant = bus_seats[seat_id]
    if current_occupant is not None:
        if current_occupant.lower() == name.lower():
            bus_seats[seat_id] = None
            return jsonify({"success": True, "message": f"Cancelled Seat {seat_id:02d}.", "seats": bus_seats})
        return jsonify({"success": False, "message": f"Seat {seat_id:02d} belongs to '{current_occupant}'.", "seats": bus_seats})
    bus_seats[seat_id] = name
    return jsonify({"success": True, "message": f"Booked Seat {seat_id:02d} for {name}.", "seats": bus_seats})

@app.route("/api/reset_bus", methods=["POST"])
def api_reset_bus():
    global bus_seats
    bus_seats = {i: None for i in range(10)}
    return jsonify({"success": True, "seats": bus_seats})

if __name__ == "__main__":
    app.run(debug=True, port=5000)