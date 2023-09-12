import tkinter as tk
import sqlite3
import handbook

#Defines a class for a draggable box
class DraggableBox(tk.Label):
    def __init__(self, parent, word, drop_boxes):
        #Initialize draggable box as a tk.label instance
        super().__init__(parent, text=word, bg='lightblue', width=20)
        
        #Set parameters of draggable box
        self.word = word
        self.drop_boxes = drop_boxes
        self.store_x = 0
        self.store_y = 0 
        
        #Bind mouse actions for dragging and dropping to the functions we need
        self.bind('<Button-1>', self.on_drag_start)
        self.bind('<B1-Motion>', self.on_drag_motion)
        self.bind('<ButtonRelease-1>', self.on_drag_release)

    #Captures & store start location of cursor and box when it is clicked on
    def on_drag_start(self, event):
        
        #event.x_root stores where the x/y coords of the mouse
        #winfo_rootx stores the absolute position of the box, winfo_x stores relative position
        #Start_x/y stores the position of the cursor relative to the box so it moves from that point
        self.start_x = event.x_root - self.winfo_rootx()
        self.start_y = event.y_root - self.winfo_rooty()
        #store_x/y stores the original position of the box so it can be returned there when needed
        self.store_x = self.winfo_x()
        self.store_y = self.winfo_y()

    def on_drag_motion(self, event):
        #Calculates the distance travelled on x & y using event.x (amount mouse cursor has moved)
        #and places the box there
        x = self.winfo_x() - self.start_x + event.x
        y = self.winfo_y() - self.start_y + event.y
        self.place(x=x, y=y)

    def on_drag_release(self, event):
        #Check if the box has been placed inside a drop box
        for drop_box in self.drop_boxes:
            if drop_box.is_inside(event.x_root, event.y_root):
                console_output(drop_box.heading, self.word)
                #If so create a label of that unit within the box and reset to original position
                drop_box.add_label(self)
                self.place(x=self.store_x, y=self.store_y)
                break
        else:
            #If the label has not been dropped in a drop box reset its position
            self.place(x=self.store_x, y=self.store_y)

class DropBox(tk.Frame):
    def __init__(self, parent, heading,id, cursor):
        #Intialize drop box as a tk.Frame
        super().__init__(parent)
        
        #Set parameters
        self.heading = heading
        self.cursor = cursor
        self.id = id
        
        #Create object and scrollbar
        self.canvas = tk.Canvas(self, bg='black', width=150, height=100)
        self.scrollbar = tk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        #Sets scrollbar to adjust position/size based on number of objects in the box
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        #Place scrollbar on the left
        self.scrollbar.pack(side='left', fill='y')
        self.labels = []
        new_label = None
        remove_button = None
        #Gets all units associated with the rule this drop box is based off & Create a label for each
        units = handbook.fetch_unit_rules(self.cursor, self.id)
        for unit in units:
            #Creates a new label same as add_label (need to try and modify add_label to integrate this properly)
            #ie just make it a function call
            new_label = tk.Label(self, text=unit, bg='lightblue', width=18)
            remove_button = tk.Button(self, text='X')
            remove_button.config(command=lambda label=new_label, button=remove_button: self.remove_label(label, button))
            lbl_id = self.canvas.create_window(0, len(self.labels) * 30, anchor='nw', window=new_label, width=120)
            btn_id = self.canvas.create_window(120, len(self.labels) * 30, anchor='nw', window=remove_button, width=30)
            self.labels.append((new_label, remove_button, lbl_id, btn_id))
            self.canvas.config(scrollregion=self.canvas.bbox('all'))
        #Create a label for the heading of the box (currently just ID - needs value added)
        tk.Label(self, text=heading, bg='white', width=20).pack(side='top')
        self.canvas.pack(side='top', fill='both', expand=True)

    def is_inside(self, x, y):
        #Get location of the box
        box_x = self.winfo_rootx()
        box_y = self.winfo_rooty()
        
        #Determine if the x/y coords provided are within bounds of the box
        return box_x <= x <= box_x + self.winfo_width() and box_y <= y <= box_y + self.winfo_height()

    def add_label(self, label):
        try:
            #Try to create a new ruleUnit link
            handbook.link_unit_rule(self.cursor, label.word, self.id)
            #Create a new label & x button for removing
            new_label = tk.Label(self, text=label.word, bg='lightblue', width=18)
            remove_button = tk.Button(self, text='X', command=lambda: self.remove_label(new_label, remove_button))
            #place button & label in the box
            lbl_id = self.canvas.create_window(0, len(self.labels) * 30, anchor='nw', window=new_label, width=120)
            btn_id = self.canvas.create_window(120, len(self.labels) * 30, anchor='nw', window=remove_button, width=30)
            #Add to labels & adjust the scrollregion of scroll_bar
            self.labels.append((new_label, remove_button, lbl_id, btn_id))
            self.canvas.config(scrollregion=self.canvas.bbox('all'))
        except sqlite3.Error:
            #If there is an exception its already in the box so we don't need to create a new label
            None
        self.cursor.execute("SELECT * FROM RuleUnits")
        results = self.cursor.fetchall()
        print(results)

    def remove_label(self, label, button):
        #Get the label & its parameters from labels
        word = label.cget("text")
        index = [i for i, (lbl, btn, lbl_id, btn_id) in enumerate(self.labels) if lbl == label][0]
        lbl, btn, lbl_id, btn_id = self.labels.pop(index)
        
        #Delete label/button from canvas & destroy them
        self.canvas.delete(lbl_id)
        self.canvas.delete(btn_id)
        label.destroy()
        button.destroy()
    
        #Adjust position of every label in the box based off its new index (ie move them up if they were below the deleted label)
        for i, (lbl, btn, lbl_id, btn_id) in enumerate(self.labels):
            self.canvas.coords(lbl_id, 0, i * 30)
            self.canvas.coords(btn_id, 120, i * 30)
        console_output_remove(self.heading, word)
        
        #Unlink the unit & rule
        handbook.unlink_unit_rule(self.cursor, word, self.heading)
        
        #Adjust scroll region
        self.canvas.config(scrollregion=self.canvas.bbox('all'))
        self.cursor.execute("SELECT * FROM RuleUnits")
        results = self.cursor.fetchall()
        print(results)

#Debugging print functions
def console_output_remove(heading, word):
    print(f"Removed from {heading}:", word)


def console_output(heading, word):
    print(f"Dropped in {heading}:", word)

def main():
    # Create the database and get the cursor
    conn = handbook.initialize_db()
    
    cursor = conn.cursor()
    
    # Initialize GUI Window & set title/dimensions
    root = tk.Tk()
    root.title("Modify major")
    root.geometry("1920x1080")
    
    # Function to refresh the screen based on the dropdown selection
    def refresh_screen():
        # Split the selected option to get name/year
        print(clicked.get())
        name, year = clicked.get().split("|")
        
        # Fetch all units and rules associated with the selected name/year
        units = handbook.fetch_all_units(cursor)
        rules = handbook.fetch_major_rules(cursor, name, year)
        mID = handbook.get_major_id(cursor, name, year)
        
        # Clear the current draggable boxes and drop boxes
        for box in draggable_boxes:
            box.destroy()
        for box in drop_boxes:
            box.destroy()
        
        # Create new draggable boxes and drop boxes based on the fetched units and rules
        draggable_boxes[:] = [DraggableBox(root, unit, drop_boxes) for unit in units]
        drop_boxes[:] = [DropBox(root, "rule " + str(rule[0])+" | value: "+str(rule[1]), rule[0], cursor) for rule in rules]
        
        # Place the new boxes on the screen
        for i, box in enumerate(draggable_boxes):
            box.place(x=50, y=50 + i * 25)
        for i, box in enumerate(drop_boxes):
            box.place(x=i//4 * 200 + 250, y= 50 + i%4 * 150)
            box.lower()
            
        drop_box_entry = tk.Entry(root)
        drop_box_entry.place(x=250, y=10)
    
        def create_draggable_box(mId):
            #Get the word input
            word = drop_box_entry.get()
            if word:
                handbook.create_rule(cursor, word)

                new_id = cursor.lastrowid
                
                handbook.link_major_rule(cursor,mId, new_id)
                #Create a new draggable box with that word & place it on the screen below all other boxes
                box = DropBox(root, "rule " + str(new_id)+" | value: "+str(word), new_id, cursor)
                num_boxes = len(drop_boxes)
                box.place(x=num_boxes//4 * 200 + 250, y = num_boxes%4 * 150 + 50)
                box.lower()
                drop_boxes.append(box)


    
        drop_box_button = tk.Button(root, text="Enter", command=lambda: create_draggable_box(mID))
        drop_box_button.place(x=375, y=10)
    
    # Dropdown menu options
    options = handbook.fetch_all_majors(cursor)
    options = [major[0] + "|" + str(major[1]) for major in options]
    
    # datatype of menu text
    clicked = tk.StringVar()
    # initial menu text
    clicked.set("Select a major or create a new one")
    
    # Create Dropdown menu
    drop = tk.OptionMenu(root, clicked, *options)
    drop.pack()
    
    # Create button to refresh the screen based on the dropdown selection
    button = tk.Button(root, text="OK", command=refresh_screen)
    button.pack()
    
    # Initialize drop_boxes list
    headings = handbook.fetch_all_rules(cursor)
    drop_boxes = [DropBox(root, "rule " + str(heading[0])+" | value: "+str(heading[1]), heading[0], cursor) for heading in headings]
    
    # Fetch all units in the db and create draggable boxes for each of them
    words = handbook.fetch_all_units(cursor)
    draggable_boxes = [DraggableBox(root, word, drop_boxes) for word in words]
    
    # Place all of the draggable boxes on the screen
    for i, box in enumerate(draggable_boxes):
        box.place(x=50, y=50 + i * 25)

    # Create and place text entry field to create new units
    entry = tk.Entry(root)
    entry.place(x=50, y=10)
    
    # Function to both create a new unit in the db & create a new physical box for the unit when a word
    # Is entered into entry
    def create_draggable_box():
        # Get the word input
        word = entry.get()
        if word:
            # Create a new draggable box with that word & place it on the screen below all other boxes
            box = DraggableBox(root, word, drop_boxes)
            box.place(x=50, y=50 + len(draggable_boxes) * 25)
            draggable_boxes.append(box)
            
            # Add new unit to the database
            handbook.create_unit(cursor, word, 6)

    # Create an enter button for creating a new unit
    button = tk.Button(root, text="Enter", command=create_draggable_box)
    button.place(x=150, y=10)

    # Start GUI Event Loop
    root.mainloop()

if __name__ == "__main__":
    main()

