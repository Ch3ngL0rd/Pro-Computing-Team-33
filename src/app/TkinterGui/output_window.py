"""
This file handles the excel preview, filtering, and output statistics
"""
import tkinter as tk

class Output_window():
    def __init__(self) -> None:
        pass

    def draw_window(self) -> None:
        root = tk.Tk()
        root.geometry("1000x400")
        root.title("Excel Preview")
        window_frame = tk.LabelFrame(root, text="Output Preview")
        window_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')


        root.mainloop()