# board2.py
import tkinter as tk
import tkinter.font as tkfont
import string
from typing import Callable, Dict, Tuple


class PlayerBoard(tk.Frame):
    """
    A 10x10 Battleship board with row/column headers for Player 2.
    - Frame-based (embed anywhere)
    - Optional on_cell_click callback: (row:int, col:int, button:tk.Button) -> None
      (rows, cols are 1..10)
    """

    def __init__(
        self,
        master=None,
        title: str = "Player 2",
        on_cell_click: Callable[[int, int, tk.Button], None] | None = None,
        cell_size: int = 3,
        header_bg: str = "#084954",   # Player 2 header color
        cell_bg: str = "#34C0D9",     # Player 2 cell color
        **kwargs
    ):
        super().__init__(master, **kwargs)

        self.title = title
        self.on_cell_click = on_cell_click
        self.cell_size = cell_size
        self.header_bg = header_bg
        self.cell_bg = cell_bg

        self.buttons: Dict[Tuple[int, int], tk.Button] = {}
        self._build()

    # ---------- public helpers ----------
    def set_cell_bg(self, row: int, col: int, color: str) -> None:
        btn = self.buttons.get((row, col))
        if btn:
            btn.configure(bg=color)

    def reset_board(self) -> None:
        for (r, c), btn in self.buttons.items():
            btn.configure(bg=self.cell_bg)

    def iter_cells(self):
        for r in range(1, 11):
            for c in range(1, 11):
                yield r, c, self.buttons[(r, c)]

    # ---------- internal UI ----------
    def _build(self) -> None:
        # Top title (pack)
        top = tk.Frame(self)
        top.pack(fill="x")
        tk.Label(
            top,
            text=f"{self.title} — Board",
            font=tkfont.Font(size=18, weight="bold"),
            padx=8, pady=6
        ).pack(fill="x")

        # Board area (grid)
        board = tk.Frame(self)
        board.pack(padx=10, pady=10)

        # Column headers (1..10; [0,0] is blank)
        for col in range(0, 11):
            text = f"{col}" if col > 0 else ""
            lbl = tk.Label(
                board, text=text,
                fg="white", bg=self.header_bg,
                width=self.cell_size + 3, height=self.cell_size
            )
            lbl.grid(row=0, column=col, sticky="nsew")

        # Row headers (A..J) + cells
        for row in range(1, 11):
            hdr = tk.Label(
                board, text=string.ascii_uppercase[row - 1],
                fg="white", bg=self.header_bg,
                width=self.cell_size + 3, height=self.cell_size
            )
            hdr.grid(row=row, column=0, sticky="nsew")

            for col in range(1, 11):
                btn = tk.Button(
                    board, text="", bg=self.cell_bg,
                    width=self.cell_size + 1, height=self.cell_size - 1,
                    command=lambda r=row, c=col: self._handle_click(r, c)
                )
                btn.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
                self.buttons[(row, col)] = btn

        # Responsive grid
        for i in range(12):
            board.rowconfigure(i, weight=1)
            board.columnconfigure(i, weight=1)

    def _handle_click(self, row: int, col: int) -> None:
        if self.on_cell_click:
            self.on_cell_click(row, col, self.buttons[(row, col)])


# Optional demo when run directly
if __name__ == "__main__":
    def demo_click(r, c, btn):
        btn.configure(bg="#0ea5b6" if btn.cget("bg") != "#0ea5b6" else "#2dbed6")

    root = tk.Tk()
    root.title("Board 2 Demo")
    board = PlayerBoard(root, title="Player 2", on_cell_click=demo_click)
    board.pack(fill="both", expand=True)
    root.mainloop()


