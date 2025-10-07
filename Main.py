import tkinter as tk
import string

window = tk.Tk()

window.title("Battleship")

cell_size = 3

for col in range(0, 11):
    frame = tk.Frame(
        master=window,
        relief="solid"
    )
    frame.grid(row=0, column=col, sticky="nsew")
    lab_x = tk.Label(
        master=frame, 
        text=f"{col}",
        fg="white", 
        bg="#084954",
        width=cell_size + 3, 
        height=cell_size)
    lab_x.pack()

for row in range(1, 11):
    frame = tk.Frame(
        master=window,
        relief="solid"
    )
    frame.grid(row=row, column=0, sticky="nsew")
    lab_y = tk.Label(
        master=frame, 
        text=f"{string.ascii_uppercase[row -1]}", 
        fg="white", 
        bg="#084954",
        width=cell_size + 3, 
        height=cell_size)
    lab_y.pack()

for r in range(1, 11):
    for c in range(1, 11):
        squares = tk.Frame(
            master=window,
            relief="raised",
            borderwidth=0,
        )
        squares.grid(row=r, column=c, padx=0, pady=1, sticky="nsew")
        btn_x_y = tk.Button(
            master=squares, 
            text="", 
            bg="#34C0D9",
            width=cell_size + 1, 
            height=cell_size - 1)
        btn_x_y.pack()

for i in range(11):
    window.grid_rowconfigure(i, weight=1)
for i in range(11):
    window.grid_columnconfigure(i, weight=1)     

window.mainloop()