"""
This file handles the excel preview, filtering, and output statistics
"""
import tkinter as tk
from pandastable import Table

WIDTH = 1000
HEIGHT = 400

TABLE_PADDING = 70

class Output_window():

    def __init__(self, output_df) -> None:
        """_summary_

        Args:
            output_df (pandas.DataFrame): dataframe of processed file - used for preview
        """
        self.output_df = output_df

    def draw_window(self) -> None:
        root = tk.Tk()
        root.geometry(f"{WIDTH}x{HEIGHT}")
        root.title("Output Preview")
        window_frame = tk.Frame(root)
        window_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        # flagged output
        flagged_window = tk.LabelFrame(window_frame, text="Flagged Rows")
        flagged_window.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        
        # output frame
        output_window = tk.LabelFrame(window_frame, text="Output Preview")
        output_window.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.draw_preview(output_window)

        root.mainloop()

    def draw_preview(self, frame):
        table = Table(frame, dataframe=self.output_df, width=WIDTH-TABLE_PADDING)
        table.show()