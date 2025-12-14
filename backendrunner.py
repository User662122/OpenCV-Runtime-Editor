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

        if self.app_color == chess.WHITE:
            move = self._get_best_move()
            return move if move else "Game Over"
        else:
            return ""

    def process_move(self, incoming):
        print(f"📥 Incoming: {incoming}")

        if not self.game_active:
            return "Game Over"

        # ===== UCI MOVE =====
        if self._is_uci_move(incoming):
            try:
                move = chess.Move.from_uci(incoming.strip().lower())
                if move in self.board.legal_moves:
                    self.board.push(move)
                    self.last_position_snapshot = self._get_piece_snapshot()
                    print(f"✅ Move detected: {move.uci()}")

                    if self.board.is_checkmate():
                        self.game_active = False
                        threading.Thread(target=self._delayed_game_over).start()
                        return ""

                    if self.board.turn == self.app_color:
                        ai_move = self._get_best_move()
                        print(f"🎯 AI response: {ai_move}")
                        return ai_move if ai_move else ""

                    return ""
                else:
                    return "Invalid"
            except:
                return "Invalid"

        # ===== POSITION FORMAT =====
        positions = self._parse_positions(incoming)
        if positions is None:
            return ""

        current_board_snapshot = self._get_piece_snapshot()

        if positions == current_board_snapshot:
            return ""

        if self._is_drastic_change(positions, current_board_snapshot):
            return ""

        move = self._deduce_move_from_snapshot(positions, current_board_snapshot)
        if not move:
            return ""

        print(f"✅ Move detected: {move}")

        try:
            move_obj = chess.Move.from_uci(move)
            if move_obj in self.board.legal_moves:
                self.board.push(move_obj)
                self.last_position_snapshot = self._get_piece_snapshot()
            else:
                return ""
        except:
            return ""

        if self.board.is_checkmate():
            self.game_active = False
            threading.Thread(target=self._delayed_game_over).start()
            return ""

        if self.board.turn == self.app_color:
            ai_move = self._get_best_move()
            print(f"🎯 AI response: {ai_move}")
            return ai_move if ai_move else ""

        return ""

    # ====================== HELPERS ======================

    def _is_uci_move(self, text):
        text = text.strip().lower()
        if len(text) == 4 and text[0] in 'abcdefgh' and text[1] in '12345678' and text[2] in 'abcdefgh' and text[3] in '12345678':
            return True
        if len(text) == 5 and text[0] in 'abcdefgh' and text[1] in '12345678' and text[2] in 'abcdefgh' and text[3] in '12345678' and text[4] in 'qnrb':
            return True
        return False

    def _delayed_game_over(self):
        time.sleep(8)
        print("⚠️ Game Over")

    def _get_best_move(self):
        self.ai.set_fen_position(self.board.fen())
        best_move = self.ai.get_best_move_time(2000)
        if best_move:
            move = chess.Move.from_uci(best_move)
            if move in self.board.legal_moves:
                self.board.push(move)
                if self.board.is_checkmate():
                    self.game_active = False
                    threading.Thread(target=self._delayed_game_over).start()
                return best_move
        return None

    def _parse_positions(self, txt):
        try:
            txt = txt.strip().lower()
            parts = txt.split(';') if ';' in txt else txt.split()

            white_squares = []
            black_squares = []

            for part in parts:
                if part.startswith("white:"):
                    white_squares = [s.strip() for s in part.split(":")[1].split(",") if s.strip()]
                elif part.startswith("black:"):
                    black_squares = [s.strip() for s in part.split(":")[1].split(",") if s.strip()]

            valid = {f"{f}{r}" for f in 'abcdefgh' for r in '12345678'}
            return {
                "white": sorted([s for s in white_squares if s in valid]),
                "black": sorted([s for s in black_squares if s in valid])
            }
        except:
            return None

    def _get_piece_snapshot(self):
        w, b = [], []
        for sq, p in self.board.piece_map().items():
            (w if p.color == chess.WHITE else b).append(chess.square_name(sq))
        return {"white": sorted(w), "black": sorted(b)}

    def _is_drastic_change(self, new_pos, cur_pos):
        diff = abs(
            (len(new_pos["white"]) + len(new_pos["black"])) -
            (len(cur_pos["white"]) + len(cur_pos["black"]))
        )
        return diff > 2

    def _deduce_move_from_snapshot(self, new_pos, cur_pos):
        cw, cb = set(cur_pos["white"]), set(cur_pos["black"])
        nw, nb = set(new_pos["white"]), set(new_pos["black"])

        wr, wa = cw - nw, nw - cw
        br, ba = cb - nb, nb - cb

        if wr == {"e1", "h1"} and wa == {"g1", "f1"}: return "e1g1"
        if wr == {"e1", "a1"} and wa == {"c1", "d1"}: return "e1c1"
        if br == {"e8", "h8"} and ba == {"g8", "f8"}: return "e8g8"
        if br == {"e8", "a8"} and ba == {"c8", "d8"}: return "e8c8"

        if len(wr) == len(wa) == 1 and not br and not ba:
            return list(wr)[0] + list(wa)[0]
        if len(br) == len(ba) == 1 and not wr and not wa:
            return list(br)[0] + list(ba)[0]

        if len(wr) == len(wa) == len(br) == 1:
            if list(wa)[0] in br:
                return list(wr)[0] + list(wa)[0]
        if len(br) == len(ba) == len(wr) == 1:
            if list(ba)[0] in wr:
                return list(br)[0] + list(ba)[0]

        return None


brain = ChessBrain()

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

ngrok.set_auth_token("31TWswIKgSWHAfejOFT6s8mcW69_4UCxySRXzy6Si8mDHn9zn")
port = 5000
public_url = ngrok.connect(port)

print("✅ BACKEND LIVE!")
print("🌍 Public URL:", public_url)

app.run(host="0.0.0.0", port=port)