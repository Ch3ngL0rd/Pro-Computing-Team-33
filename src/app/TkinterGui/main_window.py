import tkinter as tk
from tkinter import filedialog

import os

from app.TkinterGui.output_window import Output_window
from app.TkinterGui.major_edit_window import Major_edit_window


class Main_window():
    def __init__(self, marks_processor, handbook_db) -> None:
        self.root = tk.Tk()
        self.marks_processor = marks_processor
        self.handbook_db = handbook_db

        # set default path to home
        # if output path is set first - keep the same
        # else if input path is set first - set output path to the same
        self.input_filepath = os.path.expanduser("~")
        self.output_filepath = None

        self.process_file_button = None


    def draw_window(self):
        self.root.geometry("1000x400")
        self.root.title("BE(Hons) - Marks Processor")
        window_frame = tk.Frame(self.root)
        window_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')


        # Menu frame
        menu_frame = tk.LabelFrame(window_frame, text="Menu")
        menu_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        menu_frame_button_options = {"pady":5, "padx":5,}

        modify_handbook_button = tk.Button(menu_frame, text="Modify Handbook",
                                           command=self.open_major_edit_window)
        modify_handbook_button.grid(row=0, column=1, sticky='w', **menu_frame_button_options)


        # File selection frame
        file_select_frame = tk.LabelFrame(window_frame, text="File Processing")
        file_select_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        file_select_button_width = 10
        file_select_button_options = {"pady":5, "padx":5, "sticky":'ew'}
        file_select_label_options = {"pady":5, "padx":5, "sticky":'w'}

        input_file_button = tk.Button(
            file_select_frame, width=file_select_button_width, text="Input File",
            command=lambda: self.select_input_file(input_file_label)
        )
        input_file_button.grid(row=0, column=0, **file_select_button_options)

        input_file_label = tk.Label(file_select_frame, text="Selected Input File:")
        input_file_label.grid(row=0, column=1, **file_select_label_options)

        output_file_button = tk.Button(
            file_select_frame, width=file_select_button_width, text="Output File",
            command=lambda: self.select_output_file(output_file_label)
        )
        output_file_button.grid(row=1, column=0, **file_select_button_options)

        output_file_label = tk.Label(file_select_frame, text="Selected Output File:")
        output_file_label.grid(row=1, column=1, **file_select_label_options)


        # make sure this is grey or not submittable until both input and output variables are specified
        self.process_file_button = tk.Button(
            file_select_frame, width=file_select_button_width, text="Process",
            command=lambda: self.process_file(process_file_label)
        )
        self.process_file_button.grid(row=2, column=0, **file_select_button_options)
        self.process_file_button.config(state="disabled")

        process_file_label = tk.Label(file_select_frame, text="")
        process_file_label.grid(row=2, column=1, **file_select_label_options)

        # Configure row and column weights to make frames expand
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        window_frame.grid_rowconfigure(1, weight=1)
        window_frame.grid_columnconfigure(0, weight=1)
        menu_frame.grid_rowconfigure(1, weight=1)
        menu_frame.grid_columnconfigure(1, weight=1)

        self.root.mainloop()

    
    def are_files_selected(self):
        return os.path.isfile(self.input_filepath) and self.output_filepath


    def select_input_file(self, label):
        truncate_value = 30 # 30 characters

        try:
            file_path = filedialog.askopenfilename(
                title="Select a File",
                filetypes=[("Excel Files", "*.xlsx")],
                initialdir=self.input_filepath
            )
            self.input_filepath = file_path

            # if output filepath is None - set it to same as input
            if self.output_filepath: self.output_filepath = file_path

            label.config(text=f"Selected Input File: ...{self.input_filepath[-truncate_value:]}")

            if self.are_files_selected():
                self.process_file_button.config(state="normal")

            return file_path
        except Exception as e:
            print(f"Error: {str(e)}")
            return None


    def select_output_file(self, label):
        truncate_value = 30 # 30 characters

        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx")],
                initialdir=self.output_filepath
            )
            self.output_filepath = file_path
            label.config(text=f"Selected Output File: ...{self.output_filepath[-truncate_value:]}")

            if self.are_files_selected():
                self.process_file_button.config(state="normal")

            return file_path
        except Exception as e:
            print(f"Error: {str(e)}")
            return None
        

    def process_file(self, label):
        try:
            output_df = self.marks_processor.process_file(self.input_filepath, self.output_filepath)
            label.config(text=f"Success!")

            output_window = Output_window(output_df)
            output_window.draw_window()

        except IsADirectoryError:
            label.config(text=f"Input file not selected")

        except Exception as e:
            print(str(e))
            if not (self.input_filepath and self.output_filepath):
                label.config(text=f"File not selected")
            else:
                label.config(text=f"Something went wrong :(")

    
    def open_major_edit_window(self):
        try:
            major_edit_window = Major_edit_window(handbook_db=self.handbook_db, root=self.root)
            major_edit_window.initialize_UI()
        except Exception as e:
            print(e)

