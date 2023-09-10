import tkinter as tk
from tkinter import filedialog

# Global variable to store absolute file path 
absolute_file_path = ""

def open_file():
    try:
        file_path = filedialog.askopenfilename()
        if file_path:
            # Storing 'file_path' in 'absolute_file_path'
            absolute_file_path = file_path 
            file_label.config(text=f"Selected File: {file_path}")
    except Exception as e:
        file_label.config(text=f"Error: {str(e)}")

# Window settings
root = tk.Tk()
root.title("File Selector")
root.geometry("300x250")  # Set the initial size to 400x200 (width x height)

# Frame for holding button and label 
frame = tk.Frame(root)
frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame in the window

# Open file button
open_button = tk.Button(frame, text="Open File", command=open_file)
open_button.pack(pady=10)  # Add vertical padding to center the button

# Opened file path label
file_label = tk.Label(frame, text="Selected File: None")
file_label.pack(pady=10)  # Add vertical padding to center the label

root.mainloop()