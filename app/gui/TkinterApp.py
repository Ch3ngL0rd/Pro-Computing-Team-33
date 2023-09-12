import tkinter as tk
from tkinter import filedialog

import os

from app.logic.calculate import calculations


class TkinterApp():
    def __init__(self) -> None:
        # set default path to home
        self.input_filepath = os.path.expanduser("~")
        self.output_filepath = os.path.expanduser("~")


    def run_tkinter_app(self):
        root = tk.Tk()
        root.geometry("1000x400")
        root.title("BE(Hons) - Marks Processor")
        window_frame = tk.Frame(root)
        window_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')


        # Menu frame
        menu_frame = tk.LabelFrame(window_frame, text="Menu")
        menu_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        menu_frame_button_options = {"pady":5, "padx":5,}

        settings_button = tk.Button(menu_frame, text="Settings", command=root.quit)
        settings_button.grid(row=0, column=0, sticky='w', **menu_frame_button_options)

        modify_handbook_button = tk.Button(menu_frame, text="Modify Handbook", command=root.quit)
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
        process_file_button = tk.Button(
            file_select_frame, width=file_select_button_width, text="Process",
            command=lambda: self.process_file(process_file_label)
        )
        process_file_button.grid(row=2, column=0, **file_select_button_options)
        process_file_label = tk.Label(file_select_frame, text="")
        process_file_label.grid(row=2, column=1, **file_select_label_options)

        # Configure row and column weights to make frames expand
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        window_frame.grid_rowconfigure(1, weight=1)
        window_frame.grid_columnconfigure(0, weight=1)
        menu_frame.grid_rowconfigure(1, weight=1)
        menu_frame.grid_columnconfigure(1, weight=1)

        root.mainloop()


    def select_input_file(self, label):
        truncate_value = 30 # 30 characters

        try:
            file_path = filedialog.askopenfilename(
                title="Select a File",
                filetypes=[("Excel Files", "*.xlsx")],
                initialdir=self.input_filepath
            )
            self.input_filepath = file_path
            label.config(text=f"Selected Input File: ...{self.input_filepath[-truncate_value:]}")

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

            return file_path
        except Exception as e:
            print(f"Error: {str(e)}")
            return None
        

    def process_file(self, label):
        try:
            calculations(self.input_filepath, self.output_filepath)
            label.config(text=f"Success!")
        except:
            label.config(text=f"Something went wrong :(")

