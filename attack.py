import sys
import os
import json

print("[DEBUG] attack.py launched with args:", sys.argv)
sys.stdout.flush()

p1_boats = None
p2_boats = None

if len(sys.argv) > 1:
    setup_path = sys.argv[1]
    print("[DEBUG] Loading placements from:", setup_path)
    if os.path.exists(setup_path):
        try:
            with open(setup_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            p1_boats = data.get("p1_boats", [])
            p2_boats = data.get("p2_boats", [])
            print("[DEBUG] Loaded P1:", len(p1_boats))
            print("[DEBUG] Loaded P2:", len(p2_boats))
        except Exception as e:
            print("[ERROR] Could not load boat data:", e)
        # ⚠️ Don’t delete the file immediately! Only clean up at the end.
    else:
        print("[ERROR] JSON file not found:", setup_path)
else:
    print("[DEBUG] No setup file path received.")

import tkinter as tk
import tkinter.font as tkfont
from typing import List, Tuple, Dict, Set

from board1 import PlayerBoard as Player1Board
from board2 import PlayerBoard as Player2Board



# --- Colors ---
HIT_COLOR = "#ef4444"
MISS_COLOR = "#ffffff"
SHIP_COLOR = "#879091"
SUNK_COLOR = "#7f1d1d"

# --- Types ---
Boat = List[Tuple[int, int]]
Fleet = List[Boat]


# ============================================================
# AttackTurnView
# ============================================================
class AttackTurnView(tk.Frame):
    """Single player's attack turn."""

    def __init__(self, master, player_index: int,
                 p_own_boats: Fleet, p_enemy_boats: Fleet,
                 own_board_cls, enemy_board_cls,
                 seen_attacks_by_player: Set[Tuple[int, int]],
                 on_attack_done):
        super().__init__(master)
        self.player_index = player_index
        self.on_attack_done = on_attack_done
        self.own_boats = p_own_boats
        self.enemy_boats = p_enemy_boats

        self.enemy_boat_remaining: Dict[int, Set[Tuple[int, int]]] = {
            i: set(b) for i, b in enumerate(self.enemy_boats)
        }
        self.attacks_by_this_player = set(seen_attacks_by_player)
        self._has_attacked_this_turn = False
        self.attack_result = None

        self._build_ui(own_board_cls, enemy_board_cls)

    def _build_ui(self, own_board_cls, enemy_board_cls):
        # ==== Top bar ====
        top = tk.Frame(self)
        top.pack(fill="x", pady=(6, 6))
        top.columnconfigure(0, weight=1)
        top.columnconfigure(1, weight=0)
        top.columnconfigure(2, weight=1)

        tk.Label(top, text=f"Player {self.player_index} — Your turn",
                 font=tkfont.Font(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=8)

        self.btn_continue = tk.Button(
            top, text="Continue (Enter)", state="disabled",
            bg="#0ea5b6", fg="white", font=tkfont.Font(size=12, weight="bold"),
            command=self._on_continue
        )
        self.btn_continue.grid(row=0, column=1, padx=10)

        self.message_var = tk.StringVar(value="")
        tk.Label(top, textvariable=self.message_var, fg="#a00")\
            .grid(row=0, column=2, sticky="e", padx=8)

        # Enter = Continue
        self.bind("<Return>", lambda e: self._on_continue() 
                if self.btn_continue["state"] == "normal" else None)
        self.focus_set()

        # ==== Boards ====
        boards = tk.Frame(self)
        boards.pack(fill="both", expand=True, padx=10, pady=10)

        # Left: own board (disabled)
        own_frame = tk.Frame(boards)
        own_frame.pack(side="left", fill="both", expand=True)
        self.own_board = own_board_cls(master=own_frame,
                                       title=f"Player {self.player_index} (Your ships)",
                                       on_cell_click=None)
        self.own_board.pack(fill="both", expand=True)
        self._reveal_own_ships()

        # Right: attack board
        enemy_frame = tk.Frame(boards)
        enemy_frame.pack(side="right", fill="both", expand=True)
        self.enemy_board = enemy_board_cls(master=enemy_frame,
                                           title="Opponent (attack board)",
                                           on_cell_click=lambda r, c, b: self._attack_cell(r, c, b))
        self.enemy_board.pack(fill="both", expand=True)

        # Restore previous attacks
        if self.player_index == 1:
            prev_results = self.master.attack_results_by_p1
        else:
            prev_results = self.master.attack_results_by_p2

        for (r, c), was_hit in prev_results.items():
            self._mark_attack_on_enemy_board(r, c, hit=was_hit)

        self._enable_enemy_buttons()

        # Bottom feedback
        bottom = tk.Frame(self)
        bottom.pack(fill="x", pady=(4, 4))
        self.feedback_var = tk.StringVar(value="")
        tk.Label(bottom, textvariable=self.feedback_var, fg="#444").pack(side="left", padx=8)

    def _reveal_own_ships(self):
        self.own_board.reset_board()
        for boat in self.own_boats:
            for (r, c) in boat:
                self.own_board.set_cell_bg(r, c, SHIP_COLOR)
        for _, _, btn in self.own_board.iter_cells():
            btn.configure(state="disabled")

    def _enable_enemy_buttons(self):
        for r, c, btn in self.enemy_board.iter_cells():
            btn.configure(state="normal" if (r, c) not in self.attacks_by_this_player else "disabled")

    def _attack_cell(self, row: int, col: int, btn: tk.Button):
        if self._has_attacked_this_turn or (row, col) in self.attacks_by_this_player:
            return
        coord = (row, col)
        self.attacks_by_this_player.add(coord)
        self._has_attacked_this_turn = True

        # Check hit/sunk
        hit, sunk, sunk_boat_id = False, False, None
        for bid, remaining in self.enemy_boat_remaining.items():
            if coord in remaining:
                hit = True
                remaining.remove(coord)
                if not remaining:
                    sunk = True
                    sunk_boat_id = bid
                break

        # Color cells
        self._mark_attack_on_enemy_board(row, col, hit=hit)
        if sunk and sunk_boat_id is not None:
            for (rr, cc) in self.enemy_boats[sunk_boat_id]:
                self._mark_attack_on_enemy_board(rr, cc, hit=True)

        for _, _, b in self.enemy_board.iter_cells():
            b.configure(state="disabled")

        self.btn_continue.configure(state="normal")
        self.attack_result = (coord, hit, sunk, sunk_boat_id)
        self._flash("Hit!" if hit else "Miss.")

    def _mark_attack_on_enemy_board(self, r, c, hit: bool):
        btn = self.enemy_board.buttons[(r, c)]
        btn.configure(bg=HIT_COLOR if hit else MISS_COLOR, state="disabled")

    def _flash(self, msg):
        self.feedback_var.set(msg)
        self.after(1200, lambda: self.feedback_var.set(""))

    def _on_continue(self):
        print(f"[DEBUG] Continue pressed by Player {self.player_index} -> {self.attack_result}")
        if str(self.btn_continue.cget("state")) != "normal":
            return
        self.unbind("<Return>")
        self.after(0, lambda: self.on_attack_done(self.player_index, self.attack_result))




# ============================================================
# Intermission
# ============================================================
class IntermissionView(tk.Frame):
    def __init__(self, master, player_index: int, on_continue, result_text: str | None = None):
        super().__init__(master)
        self.on_continue = on_continue

        # Title: who’s up next
        tk.Label(
            self,
            text=f"Are you ready Player {player_index}?",
            font=tkfont.Font(size=18, weight="bold")
        ).pack(pady=(40, 8))

        # Last attack result (from previous player), visible to the next player
        if result_text:
            tk.Label(
                self,
                text=result_text,
                font=tkfont.Font(size=14),
                fg="#333"
            ).pack(pady=(0, 16))

        # Continue
        self.btn_continue = tk.Button(
            self,
            text="Continue (Enter)",
            font=tkfont.Font(size=14, weight="bold"),
            bg="#0ea5b6",
            fg="white",
            command=self._go
        )
        self.btn_continue.pack(pady=8)

        # Bind Enter locally
        self.bind("<Return>", lambda e: self._go())
        self.focus_set()

    def _go(self):
        self.unbind("<Return>")
        if callable(self.on_continue):
            self.on_continue()




# ============================================================
# Victory Screen
# ============================================================
class VictoryView(tk.Frame):
    def __init__(self, master, winner: int, p1_hits: int, p2_hits: int, on_restart, on_quit):
        super().__init__(master)
        self.configure(bg="white")
        tk.Label(self, text=f"🏆 Player {winner} Wins! 🏆",
                 font=tkfont.Font(size=28, weight="bold"), bg="white").pack(pady=40)

        tk.Label(self, text=f"Player 1 hits: {p1_hits}", font=tkfont.Font(size=14), bg="white").pack()
        tk.Label(self, text=f"Player 2 hits: {p2_hits}", font=tkfont.Font(size=14), bg="white").pack(pady=(0, 20))

        tk.Button(self, text="Play Again", bg="#0ea5b6", fg="white",
                  font=tkfont.Font(size=14, weight="bold"), command=on_restart).pack(pady=10)
        tk.Button(self, text="Quit", bg="#b91c1c", fg="white",
                  font=tkfont.Font(size=14, weight="bold"), command=on_quit).pack()


# ============================================================
# AttackApp
# ============================================================
class AttackApp(tk.Tk):
    """Main controller for alternating turns and victory check."""

    def __init__(self, p1_boats=None, p2_boats=None):
        super().__init__()
        self.title("Battleship — Attack Phase")
        self.geometry("1280x820")
        self.after(200, self.focus_force)
        self.after(250, self.lift)

        if p1_boats and p2_boats:
            print("[DEBUG] Using provided fleets from setup phase.")
            self.p1_boats = p1_boats
            self.p2_boats = p2_boats
        else:
            print("[INFO] Using demo fleets (no data passed).")
            self.p1_boats = p1_boats or [
                [(1,1),(1,2),(1,3),(1,4),(1,5)],
                [(3,1),(3,2),(3,3),(3,4)],
                [(5,1),(5,2),(5,3)],
                [(7,1),(7,2),(7,3)],
                [(9,1),(9,2)]
            ]
            self.p2_boats = p2_boats or [
                [(2,1),(2,2),(2,3),(2,4),(2,5)],
                [(4,1),(4,2),(4,3),(4,4)],
                [(6,1),(6,2),(6,3)],
                [(8,1),(8,2),(8,3)],
                [(10,1),(10,2)]
            ]

        self.p1_remaining = {i: set(b) for i, b in enumerate(self.p1_boats)}
        self.p2_remaining = {i: set(b) for i, b in enumerate(self.p2_boats)}

        self.attacks_by_p1, self.attacks_by_p2 = set(), set()
        self.attack_results_by_p1, self.attack_results_by_p2 = {}, {}
        self.last_attack_info_for_player = {1: None, 2: None}
        self.current_player = 1
        self.current_view = None
        self._show_turn_for_player(1)

    def _swap(self, view: tk.Frame):
        if self.current_view:
            self.current_view.pack_forget()
            self.current_view.destroy()
        self.current_view = view
        self.current_view.pack(fill="both", expand=True)

    def _show_turn_for_player(self, idx: int):
        if idx == 1:
            own, enemy = self.p1_boats, self.p2_boats
            own_cls, enemy_cls = Player1Board, Player2Board
            seen = self.attacks_by_p1
            remaining = self.p1_remaining
        else:
            own, enemy = self.p2_boats, self.p1_boats
            own_cls, enemy_cls = Player2Board, Player1Board
            seen = self.attacks_by_p2
            remaining = self.p2_remaining

        view = AttackTurnView(self, idx, own, enemy, own_cls, enemy_cls, seen, self._handle_attack_done)
        last = self.last_attack_info_for_player[idx]
        if last:
            _, coord, hit, _, _ = last
            view.message_var.set("You have been attacked. (A hit occurred)" if hit
                                 else "You have been attacked. (It was a miss)")
            for boat in own:
                for r, c in boat:
                    if not any((r, c) in rem for rem in remaining.values()):
                        view.own_board.set_cell_bg(r, c, HIT_COLOR)
        self._swap(view)

    def _handle_attack_done(self, attacker_idx: int, attack_result):
        try:
            if not attack_result:
                return
            coord, hit, sunk, sunk_boat_id = attack_result
            defender = 2 if attacker_idx == 1 else 1

        # record attacker’s shot
            if attacker_idx == 1:
                self.attacks_by_p1.add(coord)
                self.attack_results_by_p1[coord] = hit
            else:
                self.attacks_by_p2.add(coord)
                self.attack_results_by_p2[coord] = hit

        # update defender remaining
            remaining = self.p1_remaining if defender == 1 else self.p2_remaining
            for rem in remaining.values():
                if coord in rem:
                    rem.discard(coord)
                    break

            self.last_attack_info_for_player[defender] = (attacker_idx, coord, hit, sunk, sunk_boat_id)

        # Intermission (no popups)
            msg = f"Player {attacker_idx} attacked {coord}: {'Hit!' if hit else 'Miss!'}"
            self._swap(IntermissionView(self, defender, lambda: self._show_turn_for_player(defender), result_text=msg))

        except Exception as e:
            import traceback
            import sys
            traceback.print_exc(file=sys.stderr)
        # Optional: show a small messagebox to surface the error
            try:
                import tkinter.messagebox as mbox
                mbox.showerror("Error", f"Attack flow failed:\n{e}")
            except Exception:
                pass


    def _all_sunk(self, player_idx: int) -> bool:
        remaining = self.p1_remaining if player_idx == 1 else self.p2_remaining
        return all(len(s) == 0 for s in remaining.values())

    def _show_victory(self, winner: int):
        p1_hits = sum(1 for hit in self.attack_results_by_p1.values() if hit)
        p2_hits = sum(1 for hit in self.attack_results_by_p2.values() if hit)
        self._swap(VictoryView(self, winner, p1_hits, p2_hits,
                               on_restart=self._restart, on_quit=self.destroy))

    def _restart(self):
        self.destroy()
        AttackApp().mainloop()

if __name__ == "__main__":
    app = AttackApp(p1_boats, p2_boats)
    app.mainloop()
    # Clean up the temp file only after the window closes
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        os.remove(sys.argv[1])

# ============================================================
# Run
# ============================================================
if __name__ == "__main__":
    app = AttackApp(p1_boats, p2_boats)
    app.mainloop()

