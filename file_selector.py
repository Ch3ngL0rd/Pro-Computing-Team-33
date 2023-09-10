import tkinter as tk
from tkinter import filedialog

def open_file():
    try:
        file_path = filedialog.askopenfilename()
        return file_path  # Return the file_path if a file is selected
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def run_tkinter_app():
    root = tk.Tk()
    root.title("File Selector")
    root.geometry("300x250")

    frame = tk.Frame(root)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    open_button = tk.Button(frame, text="Open File", command=root.quit)
    open_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    selected_file_path = open_file()
    if selected_file_path:
        print(f"Selected File: {selected_file_path}")