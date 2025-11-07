import tkinter as tk
import tkinter.font as tkfont
from typing import List, Tuple

from board1 import PlayerBoard as Player1Board
from board2 import PlayerBoard as Player2Board

BOAT_SIZES = [5, 4, 3, 3, 2]  # standard fleet


# ----------------------------- Reusable screens -----------------------------

class IntermissionView(tk.Frame):
    """Blank screen with a single centered button to continue."""
    def __init__(self, master, button_text: str, on_continue):
        super().__init__(master)
        self.on_continue = on_continue
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        btn = tk.Button(
            self, text=button_text,
            font=tkfont.Font(size=16, weight="bold"),
            command=self.on_continue, padx=25, pady=10
        )
        btn.grid(row=1, column=0, pady=40)


class PlacementView(tk.Frame):
    """One player's ship placement screen."""
    def __init__(self, master, player_name: str, board_cls, on_confirm):
        super().__init__(master)
        self.player_name = player_name
        self.board_cls = board_cls
        self.on_confirm = on_confirm

        # placement state
        self.boat_sizes = [5, 4, 3, 3, 2]
        self.current_index = 0
        self.orientation = tk.StringVar(value="H")
        self.occupied = set()
        self.placed_boats = []

        self._build_ui()
        self._bind_keys()

    # -------------------- UI --------------------
    def _build_ui(self):
        # Header
        tk.Label(
            self,
            text=f"{self.player_name} — Place your ships",
            font=tkfont.Font(size=20, weight="bold"),
            pady=6
        ).pack()

        # Status text
        self.status_var = tk.StringVar()
        self._update_status()
        tk.Label(self, textvariable=self.status_var).pack(pady=(0, 5))

        # Tools row
        tools = tk.Frame(self)
        tools.pack(fill="x", padx=10, pady=(6, 0))

        btn_style = {
            "bg": "#0ea5b6",
            "fg": "white",
            "font": tkfont.Font(size=11, weight="bold"),
            "width": 16,
            "height": 1,
            "relief": "raised",
            "bd": 2
        }

        self.btn_undo = tk.Button(tools, text="Undo last ship (U)", command=self._undo_last, **btn_style)
        self.btn_undo.pack(side="left", padx=(0, 5))

        self.btn_clear = tk.Button(tools, text="Clear all (C)", command=self._clear_all, **btn_style)
        self.btn_clear.pack(side="left", padx=(0, 5))

        self.rotate_label = tk.Label(
            tools, text="Rotate (R)",
            font=tkfont.Font(size=11, weight="bold"),
            fg="#0ea5b6"
        )
        self.rotate_label.pack(side="left", padx=(10, 0))

        self.btn_continue = tk.Button(
            tools, text="Continue (Enter)", command=self._confirm, **btn_style
        )

        orient_frame = tk.Frame(tools)
        orient_frame.pack(side="right")
        tk.Label(orient_frame, text="Orientation:", font=tkfont.Font(size=11, weight="bold"),
                 fg="#0ea5b6").pack(side="left", padx=(0, 6))
        tk.Radiobutton(orient_frame, text="Horizontal", font=tkfont.Font(size=11, weight="bold"),
                       fg="#0ea5b6", value="H", variable=self.orientation).pack(side="left")
        tk.Radiobutton(orient_frame, text="Vertical", font=tkfont.Font(size=11, weight="bold"),
                       fg="#0ea5b6", value="V", variable=self.orientation).pack(side="left")

        # Board
        board_wrap = tk.Frame(self)
        board_wrap.pack(fill="both", expand=True, padx=10, pady=10)
        self.board = self.board_cls(
            board_wrap,
            title=self.player_name,
            on_cell_click=self._on_cell_click
        )
        self.board.pack(fill="both", expand=True)

        # Feedback
        self.feedback_var = tk.StringVar(value="")
        tk.Label(self, textvariable=self.feedback_var, fg="#b00").pack(pady=(0, 5))

    # -------------------- Key bindings --------------------
    def _bind_keys(self):
        self.bind_all("<Key-r>", lambda e: self._toggle_orientation())
        self.bind_all("<Key-R>", lambda e: self._toggle_orientation())
        self.bind_all("<Key-u>", lambda e: self._undo_last())
        self.bind_all("<Key-U>", lambda e: self._undo_last())
        self.bind_all("<Key-c>", lambda e: self._clear_all())
        self.bind_all("<Key-C>", lambda e: self._clear_all())
        self.bind_all("<Return>", lambda e: self._confirm())

    # -------------------- Placement logic --------------------
    def _on_cell_click(self, row, col, btn):
        if self.current_index >= len(self.boat_sizes):
            return

        size = self.boat_sizes[self.current_index]
        dr, dc = (0, 1) if self.orientation.get() == "H" else (1, 0)
        cells = [(row + i * dr, col + i * dc) for i in range(size)]

        if not all(1 <= r <= 10 and 1 <= c <= 10 for r, c in cells):
            self._flash_feedback("Ship would go out of bounds.")
            return
        if any(c in self.occupied for c in cells):
            self._flash_feedback("Ships cannot overlap.")
            return

        for r, c in cells:
            self.board.set_cell_bg(r, c, "#879091")
            self.occupied.add((r, c))
        self.placed_boats.append(cells)
        self.current_index += 1

        self._update_status()
        self._maybe_show_continue()

    def _undo_last(self):
        if not self.placed_boats:
            return
        last = self.placed_boats.pop()
        for r, c in last:
            self.occupied.discard((r, c))
            self.board.set_cell_bg(r, c, self.board.cell_bg)
        self.current_index = max(0, self.current_index - 1)
        self._update_status()
        self._maybe_show_continue()

    def _clear_all(self):
        for boat in self.placed_boats:
            for r, c in boat:
                self.board.set_cell_bg(r, c, self.board.cell_bg)
        self.occupied.clear()
        self.placed_boats.clear()
        self.current_index = 0
        self._update_status()
        self._maybe_show_continue()

    def _toggle_orientation(self):
        self.orientation.set("V" if self.orientation.get() == "H" else "H")
        self._flash_feedback(f"Orientation: {self.orientation.get()}")

    # -------------------- Status & Continue button --------------------
    def _update_status(self):
        if self.current_index < len(self.boat_sizes):
            size = self.boat_sizes[self.current_index]
            self.status_var.set(f"{self.player_name}: Place ship of size {size}")
        else:
            self.status_var.set(f"{self.player_name}: All ships placed!")

    def _maybe_show_continue(self):
        if self.current_index >= len(self.boat_sizes):
            if self.rotate_label.winfo_ismapped():
                self.rotate_label.pack_forget()
            if not self.btn_continue.winfo_ismapped():
                self.btn_continue.pack(side="left", padx=(10, 0))
        else:
            if self.btn_continue.winfo_ismapped():
                self.btn_continue.pack_forget()
            if not self.rotate_label.winfo_ismapped():
                self.rotate_label.pack(side="left", padx=(10, 0))

    def _flash_feedback(self, msg):
        self.feedback_var.set(msg)
        self.after(1500, lambda: self.feedback_var.set(""))

    def _confirm(self):
        if self.current_index < len(self.boat_sizes):
            self._flash_feedback("Place all ships first!")
            return
        print(f"[DEBUG] {self.player_name} pressed Continue with {len(self.placed_boats)} ships.")
        self.on_confirm(self.player_name, [list(b) for b in self.placed_boats])


# ----------------------------- Turn-based app -----------------------------

class BattleshipSetupApp(tk.Tk):
    """
    Turn-based setup controller:
      1) Player 1 places boats -> confirms
      2) Intermission ("Are you ready Player 2?") -> continue
      3) Player 2 places boats -> confirms
      4) Done screen (hook your battle phase here)
    """
    def __init__(self):
        super().__init__()
        self.title("Battleship — Setup Phase")
        self.geometry("1000x820")

        self.p1_boats: List[List[Tuple[int, int]]] = []
        self.p2_boats: List[List[Tuple[int, int]]] = []

        self.current_view: tk.Frame | None = None

        print("[DEBUG] App init -> show Player 1")
        self._show_player1()

    # ---------- view switching ----------
    def _swap(self, view: tk.Frame):
        if self.current_view:
            self.current_view.pack_forget()
            self.current_view.destroy()
        self.current_view = view
        self.current_view.pack(fill="both", expand=True)

    # ---------- stages ----------
    def _show_player1(self):
        print("[DEBUG] Showing Player 1 placement screen")
        view = PlacementView(self, "Player 1", Player1Board, self._confirmed)
        self._swap(view)

    def _show_intermission(self):
        print("[DEBUG] Showing intermission -> prompt Player 2")
        view = IntermissionView(self, "Are you ready Player 2?", self._show_player2)
        self._swap(view)

    def _show_player2(self):
        print("[DEBUG] Showing Player 2 placement screen")
        view = PlacementView(self, "Player 2", Player2Board, self._confirmed)
        self._swap(view)

    def _show_done(self):
        print("[DEBUG] Setup complete -> showing summary")
        done = tk.Frame(self)
        tk.Label(done, text="Setup complete!",
                 font=tkfont.Font(size=20, weight="bold")).pack(pady=10)
        tk.Label(done, text=f"Player 1 ships: {sum(len(b) for b in self.p1_boats)} cells").pack()
        tk.Label(done, text=f"Player 2 ships: {sum(len(b) for b in self.p2_boats)} cells").pack()
        tk.Label(done, text="Starting Attack Phase...", font=tkfont.Font(size=14)).pack(pady=10)
        self._swap(done)
        self.after(1000, self._start_attack_phase)

    def _start_attack_phase(self):
        from attack import AttackApp  # avoid circular import
        self.destroy()
        AttackApp(self.p1_boats, self.p2_boats).mainloop()

    # ---------- callback ----------
    def _confirmed(self, who, placements):
        print(f"[DEBUG] _confirmed called by {who}")
        if who == "Player 1":
            self.p1_boats = placements
            self._show_intermission()
        else:
            self.p2_boats = placements
            self._show_done()


# ----------------------------- Run -----------------------------

if __name__ == "__main__":
    BattleshipSetupApp().mainloop()
    