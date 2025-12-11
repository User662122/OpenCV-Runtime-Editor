from flask import Flask, request
import chess
from stockfish import Stockfish
import os
from pyngrok import ngrok
import time
import threading

app = Flask(__name__)

class ChessBrain:
    def __init__(self):
        self.board = chess.Board()
        self.app_color = None
        self.game_active = False
        self.last_position_snapshot = None
        self.first_move_received = False

        self.ai = Stockfish(path=self._find_stockfish(), depth=20, parameters={
            "Threads": 4,
            "Hash": 2048,
            "Skill Level": 20,
            "UCI_LimitStrength": False
        })

    def _find_stockfish(self):
        import shutil
        possible_paths = ["/usr/games/stockfish", "/usr/bin/stockfish", "stockfish"]
        for path in possible_paths:
            if os.path.isfile(path) or os.access(path, os.X_OK):
                return path
        return shutil.which("stockfish")

    def start_game(self, color):
        color = color.strip().lower()
        if color not in ['white', 'black']:
            return "Invalid"

        self.app_color = chess.WHITE if color == 'white' else chess.BLACK
        self.board.reset()
        self.game_active = True
        self.first_move_received = False
        self.last_position_snapshot = self._get_piece_snapshot()

        # If the app is white → AI moves first
        if self.app_color == chess.WHITE:
            ai_move = self._get_best_move()
            return ai_move if ai_move else "Game Over"

        return ""

    def process_move(self, incoming):
        """
        Yeh endpoint AB sirf opponent ka move lega.
        AI ka move return NAHI karega.
        """
        print(f"📥 Incoming: {incoming}")

        if not self.game_active:
            return "Game Over"

        # If direct UCI move
        if self._is_uci_move(incoming):
            try:
                move = chess.Move.from_uci(incoming.strip().lower())
                if move in self.board.legal_moves:
                    self.board.push(move)
                    self.last_position_snapshot = self._get_piece_snapshot()
                    print(f"✔ Opponent Move: {move}")
                    return ""   # AI move yaha nahi milega
                else:
                    return "Invalid"
            except:
                return "Invalid"

        # Position-based move detection
        positions = self._parse_positions(incoming)
        if positions is None:
            return ""

        current_snapshot = self._get_piece_snapshot()

        # If same → no change
        if positions == current_snapshot:
            return ""

        # If drastic change (wrong detection)
        if self._is_drastic_change(positions, current_snapshot):
            return ""

        move = self._deduce_move_from_snapshot(positions, current_snapshot)
        if not move:
            return ""

        print(f"✔ Opponent Move (deduced): {move}")
        try:
            move_obj = chess.Move.from_uci(move)
            if move_obj in self.board.legal_moves:
                self.board.push(move_obj)
                self.last_position_snapshot = self._get_piece_snapshot()
        except:
            return ""

        return ""  # AI ka move yaha nahi bhejna

    def get_ai_move(self):
        """NAYA: Yeh function hamesha AI ka move return karega."""
        if not self.game_active:
            return ""
        ai_move = self._get_best_move()
        return ai_move if ai_move else ""

    # ============================= HELPERS =============================

    def _is_uci_move(self, text):
        text = text.strip().lower()
        if len(text) == 4 and text[0] in 'abcdefgh' and text[1] in '12345678' and text[2] in 'abcdefgh' and text[3] in '12345678':
            return True
        if len(text) == 5 and text[0] in 'abcdefgh' and text[1] in '12345678' and text[2] in 'abcdefgh' and text[3] in '12345678' and text[4] in 'qnrb':
            return True
        return False

    def _get_best_move(self):
        self.ai.set_fen_position(self.board.fen())
        best_move = self.ai.get_best_move_time(2000)
        if best_move:
            move = chess.Move.from_uci(best_move)
            if move in self.board.legal_moves:
                self.board.push(move)
                return best_move
        return None

    def _parse_positions(self, txt):
        try:
            txt = txt.strip().lower()

            if ';' in txt:
                parts = txt.split(';')
            else:
                parts = txt.split()

            white_squares = []
            black_squares = []

            for part in parts:
                part = part.strip()
                if part.startswith("white:"):
                    squares_str = part.split(":")[1]
                    white_squares = [sq.strip() for sq in squares_str.split(",") if sq.strip()]
                elif part.startswith("black:"):
                    squares_str = part.split(":")[1]
                    black_squares = [sq.strip() for sq in squares_str.split(",") if sq.strip()]

            valid_squares = {f"{file}{rank}" for file in 'abcdefgh' for rank in '12345678'}
            white_squares = [sq for sq in white_squares if sq in valid_squares]
            black_squares = [sq for sq in black_squares if sq in valid_squares]

            return {"white": sorted(white_squares), "black": sorted(black_squares)}

        except:
            return None

    def _get_piece_snapshot(self):
        w = []
        b = []
        for square, piece in self.board.piece_map().items():
            sq_name = chess.square_name(square)
            if piece.color == chess.WHITE:
                w.append(sq_name)
            else:
                b.append(sq_name)
        return {"white": sorted(w), "black": sorted(b)}

    def _is_drastic_change(self, new_pos, current_pos):
        if current_pos is None:
            return False

        cw = set(current_pos["white"])
        cb = set(current_pos["black"])
        nw = set(new_pos["white"])
        nb = set(new_pos["black"])

        removed = len(cw - nw) + len(cb - nb)
        added = len(nw - cw) + len(nb - cb)

        return added > 2 or removed > 2

    def _deduce_move_from_snapshot(self, new_pos, current_pos):
        cw = set(current_pos["white"])
        cb = set(current_pos["black"])
        nw = set(new_pos["white"])
        nb = set(new_pos["black"])

        wr = cw - nw
        wa = nw - cw
        br = cb - nb
        ba = nb - cb

        # Castling detection
        if wr == {"e1", "h1"} and wa == {"g1", "f1"}:
            return "e1g1"
        if wr == {"e1", "a1"} and wa == {"c1", "d1"}:
            return "e1c1"
        if br == {"e8", "h8"} and ba == {"g8", "f8"}:
            return "e8g8"
        if br == {"e8", "a8"} and ba == {"c8", "d8"}:
            return "e8c8"

        # Normal moves
        if len(wr) == 1 and len(wa) == 1:
            return list(wr)[0] + list(wa)[0]
        if len(br) == 1 and len(ba) == 1:
            return list(br)[0] + list(ba)[0]

        return None


brain = ChessBrain()

# ========================= ROUTES =========================

@app.route('/start', methods=['POST'])
def start():
    color = request.get_data(as_text=True).strip()
    result = brain.start_game(color)
    return result, 200, {'Content-Type': 'text/plain'}

@app.route('/move', methods=['POST'])
def move():
    msg = request.get_data(as_text=True).strip()
    result = brain.process_move(msg)
    return result, 200, {'Content-Type': 'text/plain'}

@app.route('/givemove', methods=['GET'])
def givemove():
    move = brain.get_ai_move()
    return move, 200, {'Content-Type': 'text/plain'}


ngrok.set_auth_token("31TWswIKgSWHAfejOFT6s8mcW69_4UCxySRXzy6Si8mDHn9zn")
port = 5000
public_url = ngrok.connect(port)

print("✅ BACKEND LIVE!")
print("🌍 Public URL:", public_url)
print("🕹  POST /start   ('white' or 'black')")
print("♟  POST /move    (opponent move only)")
print("🤖 GET  /givemove (AI best move)")
print("=======================================================")

app.run(host="0.0.0.0", port=port)