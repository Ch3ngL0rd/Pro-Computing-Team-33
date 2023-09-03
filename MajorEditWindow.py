import tkinter as tk
import handbook

class DraggableBox(tk.Label):
    def __init__(self, parent, word, drop_boxes):
        super().__init__(parent, text=word, bg='lightblue', width=20)
        self.word = word
        self.drop_boxes = drop_boxes
        self.bind('<Button-1>', self.on_drag_start)
        self.bind('<B1-Motion>', self.on_drag_motion)
        self.bind('<ButtonRelease-1>', self.on_drag_release)
        self.store_x = 0
        self.store_y = 0 

    def on_drag_start(self, event):
        self.start_x = event.x_root - self.winfo_rootx()
        self.start_y = event.y_root - self.winfo_rooty()
        self.store_x = self.winfo_x()
        self.store_y = self.winfo_y()

    def on_drag_motion(self, event):
        x = self.winfo_x() - self.start_x + event.x
        y = self.winfo_y() - self.start_y + event.y
        self.place(x=x, y=y)

    def on_drag_release(self, event):
        for drop_box in self.drop_boxes:
            if drop_box.is_inside(event.x_root, event.y_root):
                console_output(drop_box.heading, self.word)
                drop_box.add_label(self)
                self.place(x=self.store_x, y=self.store_y) # Reset to original position
                break
        else:
            self.place(x=self.store_x, y=self.store_y)

class DropBox(tk.Frame):
    def __init__(self, parent, heading, cursor):
        super().__init__(parent)
        self.heading = heading
        self.cursor = cursor
        self.canvas = tk.Canvas(self, bg='black', width=150, height=100)
        self.scrollbar = tk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='y')
        self.labels = []
        tk.Label(self, text=heading, bg='white', width=20).pack(side='top')
        self.canvas.pack(side='top', fill='both', expand=True)

    def is_inside(self, x, y):
        box_x = self.winfo_rootx()
        box_y = self.winfo_rooty()
        return box_x <= x <= box_x + self.winfo_width() and box_y <= y <= box_y + self.winfo_height()

    def add_label(self, label):
        new_label = tk.Label(self, text=label.word, bg='lightblue', width=18)
        remove_button = tk.Button(self, text='X', command=lambda: self.remove_label(new_label, remove_button))
        lbl_id = self.canvas.create_window(0, len(self.labels) * 30, anchor='nw', window=new_label, width=120)
        btn_id = self.canvas.create_window(120, len(self.labels) * 30, anchor='nw', window=remove_button, width=30)
        self.labels.append((new_label, remove_button, lbl_id, btn_id))
        self.canvas.config(scrollregion=self.canvas.bbox('all'))
        handbook.link_unit_rule(self.cursor, label.word, self.heading)
        self.cursor.execute("SELECT * FROM RuleUnits")
        results = self.cursor.fetchall()
        print(results)

    def remove_label(self, label, button):
        word = label.cget("text")
        index = [i for i, (lbl, btn, lbl_id, btn_id) in enumerate(self.labels) if lbl == label][0]
        lbl, btn, lbl_id, btn_id = self.labels.pop(index)
        self.canvas.delete(lbl_id)
        self.canvas.delete(btn_id)
        label.destroy()
        button.destroy()
        for i, (lbl, btn, lbl_id, btn_id) in enumerate(self.labels):
            self.canvas.coords(lbl_id, 0, i * 30)
            self.canvas.coords(btn_id, 120, i * 30)
        console_output_remove(self.heading, word)
        handbook.unlink_unit_rule(self.cursor, word, self.heading)
        self.canvas.config(scrollregion=self.canvas.bbox('all'))
        self.cursor.execute("SELECT * FROM RuleUnits")
        results = self.cursor.fetchall()
        print(results)


def console_output_remove(heading, word):
    print(f"Removed from {heading}:", word)


def console_output(heading, word):
    print(f"Dropped in {heading}:", word)

def main():
    conn = handbook.initialize_db()
    cursor = conn.cursor()
    
    root = tk.Tk()
    root.title("Drag and Drop Example")
    root.geometry("800x800")

    headings = handbook.fetch_all_rules(cursor)
    num_drop_boxes = len(headings)
    drop_boxes = [DropBox(root, heading, cursor) for heading in headings]

    for i, box in enumerate(drop_boxes):
        box.place(x=50, y=50 + i * 125)
    
    entry = tk.Entry(root)
    entry.place(x=400, y=10)
    
    def create_draggable_box():
        word = entry.get()
        if word:
            box = DraggableBox(root, word, drop_boxes)
            handbook.create_unit(cursor, word, 6)
            box.place(x=400, y=50 + len(draggable_boxes) * spacing)
            draggable_boxes.append(box)

    button = tk.Button(root, text="Enter", command=create_draggable_box)
    button.place(x=500, y=10)

    words = handbook.fetch_all_units(cursor)
    draggable_boxes = [DraggableBox(root, word, drop_boxes) for word in words]
    
    spacing = 25
    for i, box in enumerate(draggable_boxes):
        box.place(x=400, y=50 + i * spacing)

    root.mainloop()

if __name__ == "__main__":
    main()
